#!/usr/bin/env node

import { readFile, readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const workflowsDirectory = path.join(repositoryRoot, "workflows");
const schemaPath = path.join(repositoryRoot, "schemas", "workflows", "v1", "workflow.schema.json");
const recoveryDecisionsPath = path.join(repositoryRoot, "docs", "workflow-recovery-decisions.json");

function valueType(value) {
  if (Array.isArray(value)) return "array";
  if (value === null) return "null";
  return typeof value;
}

function validateJsonSchema(value, schema, location = "$") {
  const errors = [];
  const fail = (message) => errors.push(`${location}: ${message}`);

  if ("const" in schema && value !== schema.const)
    fail(`must equal ${JSON.stringify(schema.const)}`);
  if (schema.enum && !schema.enum.some((item) => Object.is(item, value)))
    fail(`must be one of ${schema.enum.map(JSON.stringify).join(", ")}`);

  if (schema.oneOf) {
    const branchErrors = schema.oneOf.map((branch) => validateJsonSchema(value, branch, location));
    const matches = branchErrors.filter((issues) => issues.length === 0).length;
    if (matches !== 1) fail(`must match exactly one schema branch (matched ${matches})`);
    return errors;
  }

  if (schema.type) {
    const actual = valueType(value);
    const matches =
      schema.type === actual ||
      (schema.type === "integer" && Number.isInteger(value)) ||
      (schema.type === "number" && typeof value === "number" && Number.isFinite(value));
    if (!matches) {
      fail(`must be ${schema.type}; received ${actual}`);
      return errors;
    }
  }

  if (typeof value === "string" && schema.minLength !== undefined) {
    if (value.length < schema.minLength)
      fail(`must contain at least ${schema.minLength} character(s)`);
  }
  if (typeof value === "number") {
    if (schema.minimum !== undefined && value < schema.minimum)
      fail(`must be >= ${schema.minimum}`);
    if (schema.maximum !== undefined && value > schema.maximum)
      fail(`must be <= ${schema.maximum}`);
  }
  if (Array.isArray(value)) {
    if (schema.minItems !== undefined && value.length < schema.minItems)
      fail(`must contain at least ${schema.minItems} item(s)`);
    if (schema.items) {
      value.forEach((item, index) => {
        errors.push(...validateJsonSchema(item, schema.items, `${location}[${index}]`));
      });
    }
  }
  if (valueType(value) === "object") {
    for (const key of schema.required ?? []) {
      if (!Object.hasOwn(value, key))
        errors.push(`${location}.${key}: required property is missing`);
    }
    for (const [key, propertySchema] of Object.entries(schema.properties ?? {})) {
      if (Object.hasOwn(value, key)) {
        errors.push(...validateJsonSchema(value[key], propertySchema, `${location}.${key}`));
      }
    }
    if (schema.additionalProperties === false) {
      const known = new Set(Object.keys(schema.properties ?? {}));
      for (const key of Object.keys(value)) {
        if (!known.has(key)) errors.push(`${location}.${key}: unknown property`);
      }
    }
  }

  return errors;
}

function validateWorkflowSemantics(workflow) {
  const errors = [];
  if (!workflow || valueType(workflow) !== "object") return errors;
  const steps = Array.isArray(workflow.steps) ? workflow.steps : [];
  const ids = new Set();
  for (const [index, step] of steps.entries()) {
    const location = `$.steps[${index}]`;
    if (!step || valueType(step) !== "object") continue;
    if (typeof step.id === "string") {
      if (ids.has(step.id)) errors.push(`${location}.id: step id must be unique`);
      ids.add(step.id);
    }
    if (Boolean(step.skill) === Boolean(step.prompt)) {
      errors.push(`${location}: requires exactly one of skill or prompt`);
    }
  }

  for (const [index, step] of steps.entries()) {
    if (!step || valueType(step) !== "object") continue;
    for (const dependency of step.dependsOn ?? []) {
      if (!ids.has(dependency)) {
        errors.push(`$.steps[${index}].dependsOn: unknown step id ${JSON.stringify(dependency)}`);
      }
    }
  }

  const state = new Map();
  const dependencies = new Map(
    steps
      .filter((step) => step && typeof step.id === "string")
      .map((step) => [step.id, step.dependsOn ?? []]),
  );
  function visit(id) {
    if (state.get(id) === "visiting") return false;
    if (state.get(id) === "done") return true;
    state.set(id, "visiting");
    for (const dependency of dependencies.get(id) ?? []) {
      if (dependencies.has(dependency) && !visit(dependency)) return false;
    }
    state.set(id, "done");
    return true;
  }
  if (![...dependencies.keys()].every(visit))
    errors.push("$.steps: dependency graph must be acyclic");

  if (workflow.finalGate && !ids.has(workflow.finalGate.stepId)) {
    errors.push("$.finalGate.stepId: must reference a workflow step");
  }

  for (const [index, derivation] of (workflow.deriveContext ?? []).entries()) {
    const condition = derivation?.when;
    if (!condition || valueType(condition) !== "object") continue;
    const count = ["equals", "in", "includes"].filter((key) =>
      Object.hasOwn(condition, key),
    ).length;
    if (count !== 1) {
      errors.push(`$.deriveContext[${index}].when: requires exactly one predicate`);
    }
  }

  return errors;
}

async function readJson(filename) {
  return JSON.parse(await readFile(filename, "utf8"));
}

async function validatePublishedCatalog() {
  const [schema, manifest, decisions] = await Promise.all([
    readJson(schemaPath),
    readJson(path.join(repositoryRoot, "manifest.json")),
    readJson(recoveryDecisionsPath),
  ]);
  const workflowEntries = manifest.workflows ?? [];
  const files = (await readdir(workflowsDirectory))
    .filter((filename) => filename.endsWith(".workflow.json"))
    .toSorted();
  const manifestPaths = new Set(workflowEntries.map((entry) => entry.path));
  const expectedPaths = new Set(files.map((filename) => `workflows/${filename}`));
  const errors = [];

  for (const entry of workflowEntries) {
    if (!expectedPaths.has(entry.path))
      errors.push(`manifest.json: missing workflow file ${entry.path}`);
  }
  for (const filename of files) {
    const repoPath = `workflows/${filename}`;
    if (!manifestPaths.has(repoPath)) errors.push(`manifest.json: ${repoPath} is not published`);
    const workflow = await readJson(path.join(workflowsDirectory, filename));
    const fileErrors = [
      ...validateJsonSchema(workflow, schema),
      ...validateWorkflowSemantics(workflow),
    ];
    const entry = workflowEntries.find((candidate) => candidate.path === repoPath);
    if (entry && entry.slug !== workflow.slug) {
      fileErrors.push(
        `manifest slug ${JSON.stringify(entry.slug)} does not match ${JSON.stringify(workflow.slug)}`,
      );
    }

    const workflowDecisions = decisions[workflow.slug];
    if (!workflowDecisions || valueType(workflowDecisions) !== "object") {
      fileErrors.push("missing recovery-decision rationale map");
    } else {
      const stepIds = new Set(workflow.steps.map((step) => step.id));
      for (const step of workflow.steps) {
        const decision = workflowDecisions[step.id];
        const expected = step.recovery ? "manual" : "disabled";
        if (
          !decision ||
          decision.policy !== expected ||
          typeof decision.rationale !== "string" ||
          decision.rationale.trim().length < 12
        ) {
          fileErrors.push(`step ${step.id}: recovery rationale must record policy ${expected}`);
        }
      }
      for (const stepId of Object.keys(workflowDecisions)) {
        if (!stepIds.has(stepId))
          fileErrors.push(`recovery rationale references unknown step ${stepId}`);
      }
    }

    errors.push(...fileErrors.map((error) => `${repoPath}: ${error}`));
  }

  return errors;
}

async function validateBrokenFixtures() {
  const schema = await readJson(schemaPath);
  const fixturesDirectory = path.join(repositoryRoot, "tests", "fixtures", "invalid");
  const expectations = {
    "dependency-cycle.workflow.json": "dependency graph must be acyclic",
    "invalid-final-gate.workflow.json": "must reference a workflow step",
    "missing-revision.workflow.json": "$.revision: required property is missing",
    "schema-violation.workflow.json": "must contain at least 1 item",
    "unknown-recovery-mode.workflow.json": 'must equal "manual"',
  };
  const errors = [];
  for (const [filename, expected] of Object.entries(expectations)) {
    const workflow = await readJson(path.join(fixturesDirectory, filename));
    const issues = [
      ...validateJsonSchema(workflow, schema),
      ...validateWorkflowSemantics(workflow),
    ];
    if (!issues.some((issue) => issue.includes(expected))) {
      errors.push(
        `${filename}: expected rejection containing ${JSON.stringify(expected)}; got ${issues.join("; ") || "no errors"}`,
      );
    }
  }
  return errors;
}

const errors =
  process.argv[2] === "--test"
    ? [...(await validatePublishedCatalog()), ...(await validateBrokenFixtures())]
    : await validatePublishedCatalog();

if (errors.length > 0) {
  console.error(errors.map((error) => `- ${error}`).join("\n"));
  process.exit(1);
}

console.log(
  process.argv[2] === "--test"
    ? "Workflow catalog and invalid-fixture checks passed."
    : "Workflow catalog validation passed.",
);
