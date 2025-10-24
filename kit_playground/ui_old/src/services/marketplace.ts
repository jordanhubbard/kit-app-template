/**
 * Marketplace Service
 * Handles template marketplace operations (stub for now)
 */

export const fetchMarketplaceTemplates = async () => {
  // In production, this would fetch from a real marketplace API
  // For now, return empty array as local templates are the focus
  return [];
};

export const downloadTemplate = async (templateId: string) => {
  // Stub implementation
  console.log(`Download template: ${templateId}`);
  return { success: true };
};