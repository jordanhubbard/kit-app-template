/**
 * Port Service
 *
 * Provides utilities for querying and validating port configurations
 * from the centralized PortRegistry on the backend.
 *
 * This service is useful for debugging connection issues and understanding
 * the service topology in development/remote modes.
 */

export interface ServiceInfo {
  name: string;
  port: number;
  host: string;
  protocol: string;
  url: string;
}

export interface XpraDisplayInfo {
  display: number;
  port: number;
  url: string;
}

export interface PortConfig {
  backend: ServiceInfo | null;
  frontend: ServiceInfo | null;
  xpra_displays: Record<string, XpraDisplayInfo>;
  default_host: string;
  remote_mode: boolean;
}

export interface PortValidation {
  [serviceName: string]: boolean;
}

class PortServiceClass {
  /**
   * Fetch current port configuration from backend.
   *
   * @returns Promise resolving to port configuration
   */
  async fetchPortConfig(): Promise<PortConfig> {
    const response = await fetch('/api/config/ports');
    if (!response.ok) {
      throw new Error(`Failed to fetch port config: ${response.statusText}`);
    }
    return await response.json();
  }

  /**
   * Validate that all registered services are reachable.
   *
   * @returns Promise resolving to validation results
   */
  async validatePorts(): Promise<PortValidation> {
    const response = await fetch('/api/config/ports/validate');
    if (!response.ok) {
      throw new Error(`Failed to validate ports: ${response.statusText}`);
    }
    return await response.json();
  }

  /**
   * Log port configuration to console for debugging.
   */
  async logPortConfig(): Promise<void> {
    try {
      const config = await this.fetchPortConfig();
      console.group('🔌 Port Configuration');
      console.log('Backend:', config.backend);
      console.log('Frontend:', config.frontend);
      console.log('Xpra Displays:', config.xpra_displays);
      console.log('Default Host:', config.default_host);
      console.log('Remote Mode:', config.remote_mode);
      console.groupEnd();
    } catch (error) {
      console.error('Failed to fetch port configuration:', error);
    }
  }

  /**
   * Log port validation results to console for debugging.
   */
  async logPortValidation(): Promise<void> {
    try {
      const validation = await this.validatePorts();
      console.group('✓ Port Validation');
      for (const [service, reachable] of Object.entries(validation)) {
        const icon = reachable ? '✓' : '✗';
        const style = reachable ? 'color: green' : 'color: red';
        console.log(`%c${icon} ${service}`, style);
      }
      console.groupEnd();
    } catch (error) {
      console.error('Failed to validate ports:', error);
    }
  }

  /**
   * Get preview URL for a specific Xpra display.
   *
   * Note: The backend typically provides the preview URL directly in the
   * /api/projects/run response. This method is for debugging/diagnostics.
   *
   * @param display - Xpra display number (default 100)
   * @returns Promise resolving to preview URL, or null if display not registered
   */
  async getPreviewUrl(display: number = 100): Promise<string | null> {
    try {
      const config = await this.fetchPortConfig();
      const displayInfo = config.xpra_displays[display.toString()];
      return displayInfo ? displayInfo.url : null;
    } catch (error) {
      console.error('Failed to get preview URL:', error);
      return null;
    }
  }
}

// Export singleton instance
export const PortService = new PortServiceClass();

// Make available globally for console debugging
if (typeof window !== 'undefined') {
  (window as any).PortService = PortService;
}

