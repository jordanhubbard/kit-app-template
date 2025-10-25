import { create } from 'zustand';

/**
 * Panel Types
 * Each panel type corresponds to a specific view/functionality
 */
export type PanelType = 
  | 'template-browser'      // Always visible - browse templates
  | 'template-detail'       // Show template details and create form
  | 'project-detail'        // Show project details and actions
  | 'project-config'        // Configure/create project
  | 'code-editor'          // Edit .kit files
  | 'build-output'         // Show build logs and progress
  | 'preview';             // Live preview/streaming

/**
 * Panel State
 */
export interface PanelState {
  id: string;
  type: PanelType;
  title: string;
  width: number;          // Width in pixels
  minWidth: number;       // Minimum width
  maxWidth?: number;      // Maximum width (optional)
  data: any;              // Panel-specific data
  isVisible: boolean;
  canClose: boolean;      // Can this panel be closed?
  canResize: boolean;     // Can this panel be resized?
}

/**
 * Panel Store State
 */
interface PanelStoreState {
  panels: PanelState[];
  activePanel: string | null;
  
  // Actions
  openPanel: (type: PanelType, data?: any, options?: Partial<PanelState>) => void;
  closePanel: (id: string) => void;
  closeAllPanels: (except?: string[]) => void;
  resizePanel: (id: string, width: number) => void;
  setActivePanel: (id: string) => void;
  updatePanelData: (id: string, data: any) => void;
  updatePanelTitle: (id: string, title: string) => void;
  getPanelById: (id: string) => PanelState | undefined;
  getPanelsByType: (type: PanelType) => PanelState[];
}

/**
 * Default panel configurations
 */
const defaultPanelConfig: Record<PanelType, Partial<PanelState>> = {
  'template-browser': {
    title: 'Templates',
    width: 280,
    minWidth: 240,
    maxWidth: 400,
    canClose: false,
    canResize: true,
  },
  'template-detail': {
    title: 'Template Details',
    width: 400,
    minWidth: 350,
    maxWidth: 600,
    canClose: true,
    canResize: true,
  },
  'project-detail': {
    title: 'Project Details',
    width: 400,
    minWidth: 350,
    maxWidth: 600,
    canClose: true,
    canResize: true,
  },
  'project-config': {
    title: 'Configuration',
    width: 500,
    minWidth: 400,
    maxWidth: 700,
    canClose: true,
    canResize: true,
  },
  'code-editor': {
    title: 'Editor',
    width: 600,
    minWidth: 400,
    maxWidth: 1000,
    canClose: true,
    canResize: true,
  },
  'build-output': {
    title: 'Build Output',
    width: 500,
    minWidth: 400,
    maxWidth: 800,
    canClose: true,
    canResize: true,
  },
  'preview': {
    title: 'Preview',
    width: 800,
    minWidth: 600,
    canClose: true,
    canResize: true,
  },
};

/**
 * Generate unique panel ID
 */
let panelIdCounter = 0;
const generatePanelId = (type: PanelType): string => {
  return `panel-${type}-${++panelIdCounter}`;
};

/**
 * Panel Store
 */
export const usePanelStore = create<PanelStoreState>((set, get) => ({
  panels: [
    // Template browser is always visible by default
    {
      id: 'panel-template-browser-0',
      type: 'template-browser',
      isVisible: true,
      data: {},
      ...defaultPanelConfig['template-browser'],
    } as PanelState,
  ],
  activePanel: 'panel-template-browser-0',
  
  openPanel: (type, data = {}, options = {}) => {
    const id = generatePanelId(type);
    const config = defaultPanelConfig[type];
    
    const newPanel: PanelState = {
      id,
      type,
      isVisible: true,
      data,
      ...config,
      ...options,
    } as PanelState;
    
    set((state) => ({
      panels: [...state.panels, newPanel],
      activePanel: id,
    }));
  },
  
  closePanel: (id) => {
    const panel = get().getPanelById(id);
    if (panel && !panel.canClose) {
      console.warn(`Panel ${id} cannot be closed`);
      return;
    }
    
    set((state) => {
      const newPanels = state.panels.filter((p) => p.id !== id);
      const newActivePanel = state.activePanel === id
        ? (newPanels[newPanels.length - 1]?.id || null)
        : state.activePanel;
      
      return {
        panels: newPanels,
        activePanel: newActivePanel,
      };
    });
  },
  
  closeAllPanels: (except = []) => {
    set((state) => {
      const newPanels = state.panels.filter(
        (p) => !p.canClose || except.includes(p.id)
      );
      
      const newActivePanel = newPanels.find((p) => p.id === state.activePanel)
        ? state.activePanel
        : (newPanels[newPanels.length - 1]?.id || null);
      
      return {
        panels: newPanels,
        activePanel: newActivePanel,
      };
    });
  },
  
  resizePanel: (id, width) => {
    set((state) => ({
      panels: state.panels.map((p) => {
        if (p.id !== id) return p;
        
        const newWidth = Math.max(
          p.minWidth,
          Math.min(width, p.maxWidth || Infinity)
        );
        
        return { ...p, width: newWidth };
      }),
    }));
  },
  
  setActivePanel: (id) => {
    set({ activePanel: id });
  },
  
  updatePanelData: (id, data) => {
    set((state) => ({
      panels: state.panels.map((p) =>
        p.id === id ? { ...p, data: { ...p.data, ...data } } : p
      ),
    }));
  },
  
  updatePanelTitle: (id, title) => {
    set((state) => ({
      panels: state.panels.map((p) =>
        p.id === id ? { ...p, title } : p
      ),
    }));
  },
  
  getPanelById: (id) => {
    return get().panels.find((p) => p.id === id);
  },
  
  getPanelsByType: (type) => {
    return get().panels.filter((p) => p.type === type);
  },
}));

