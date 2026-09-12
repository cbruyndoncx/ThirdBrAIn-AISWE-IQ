import * as fs from 'fs';
import { CodxTarget, BuildResult, ValidationResult, CodxModule } from './types';
import { loadAllModules } from './loader';
import { renderTemplate, generateDiff } from './renderer';
import { logValidationFailure, logFailureSummary } from './logger';

/**
 * Validates a single target by running all module validations
 * and comparing rendered output with disk content
 * @param target The CodxTarget to validate
 * @param rootDir The root directory (for logging)
 * @returns BuildResult indicating success or failure
 */
export async function validateTarget(
  target: CodxTarget,
  rootDir: string = process.cwd()
): Promise<BuildResult> {
  const result: BuildResult = {
    targetFile: target.targetFile,
    success: true,
    validationResults: [],
    contentMatches: false
  };

  try {
    // Load all modules
    const loadedModules = await loadAllModules(target.modules);

    // Run validate() on each module
    for (const [varName, module] of loadedModules.entries()) {
      const validationResult = await validateModule(varName, module, target.targetFile, rootDir);
      result.validationResults.push(validationResult);

      if (!validationResult.success) {
        result.success = false;
      }
    }

    // If any validation failed, stop here
    if (!result.success) {
      return result;
    }

    // Render the template
    result.renderedContent = renderTemplate(target.templateFile, loadedModules);

    // Read existing content from disk
    if (fs.existsSync(target.targetFile)) {
      result.diskContent = fs.readFileSync(target.targetFile, 'utf-8');
    } else {
      result.diskContent = '';
    }

    // Compare
    result.contentMatches = result.renderedContent === result.diskContent;

    if (!result.contentMatches) {
      result.success = false;
      result.error = 'Rendered content does not match disk content';

      // Log concise summary for analytics
      logFailureSummary('(content-mismatch)', target.targetFile, rootDir);
    }
  } catch (error) {
    result.success = false;
    result.error = error instanceof Error ? error.message : String(error);
  }

  return result;
}

/**
 * Validates a single module by running its validate() function
 * @param varName The variable name
 * @param module The loaded CodxModule
 * @param targetFile The target file (for logging)
 * @param rootDir The root directory (for logging)
 * @returns ValidationResult indicating success or failure
 */
async function validateModule(
  varName: string,
  module: CodxModule,
  targetFile: string,
  rootDir: string
): Promise<ValidationResult> {
  try {
    await module.validate();
    return {
      moduleName: varName,
      success: true
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);

    // Log concise summary for analytics
    logFailureSummary(varName, targetFile, rootDir);

    return {
      moduleName: varName,
      success: false,
      error: errorMessage,
      errorContent: module.errorContent
    };
  }
}

/**
 * Builds a target by rendering the template and writing it to disk
 * Only writes if all validations pass
 * @param target The CodxTarget to build
 * @param rootDir The root directory (for logging)
 * @returns BuildResult indicating success or failure
 */
export async function buildTarget(
  target: CodxTarget,
  rootDir: string = process.cwd()
): Promise<BuildResult> {
  const result: BuildResult = {
    targetFile: target.targetFile,
    success: true,
    validationResults: []
  };

  try {
    // Load all modules
    const loadedModules = await loadAllModules(target.modules);

    // Run validate() on each module
    for (const [varName, module] of loadedModules.entries()) {
      const validationResult = await validateModule(varName, module, target.targetFile, rootDir);
      result.validationResults.push(validationResult);

      if (!validationResult.success) {
        result.success = false;
      }
    }

    // If any validation failed, stop here (don't write)
    if (!result.success) {
      result.error = 'Validation failed, refusing to build';
      return result;
    }

    // Render the template
    result.renderedContent = renderTemplate(target.templateFile, loadedModules);

    // Write to disk
    fs.writeFileSync(target.targetFile, result.renderedContent, 'utf-8');

    result.contentMatches = true;
  } catch (error) {
    result.success = false;
    result.error = error instanceof Error ? error.message : String(error);
  }

  return result;
}
