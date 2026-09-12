import { ConfigRegistry } from '../../registry/config-registry';
import { ErrorHandler, RegistryError } from '../../utils/error-handler';
import { DisplayUtils } from '../utils/display';

/**
 * List command - shows all available configurations
 */
export class ListCommand {
  static async execute(): Promise<void> {
    await ErrorHandler.wrapAsync(async () => {
      const registry = new ConfigRegistry();

      try {
        await registry.initialize();
      } catch (error) {
        throw new RegistryError('Failed to load configuration registry', error as Error);
      }

      DisplayUtils.showAvailableConfigurations((category: string) =>
        registry.getByCategory(category)
      );
    }, 'list-command');
  }
}
