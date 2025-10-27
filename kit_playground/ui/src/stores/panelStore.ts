import { create } from 'zustand';

/**
 * Panel Types
 * Each panel type corresponds to a specific view/functionality
 */
export type PanelType =
  | 'template-sidebar'      // Always visible - compact sidebar navigation
  | 'template-grid'         // Main content - 2D grid of templates
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
  panels: PanelState[];           // Currently visible panels
  retiredPanels: PanelState[];    // Panels that slid off to the left
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

  // Carousel navigation
  scrollLeft: () => void;
  scrollRight: () => void;
  canScrollLeft: () => boolean;
  canScrollRight: () => boolean;
  checkCapacityAndRetire: () => void;
}

/**
 * Default panel configurations
 */
const defaultPanelConfig: Record<PanelType, Partial<PanelState>> = {
  'template-sidebar': {
    title: 'Templates',
    width: 260,
    minWidth: 200,
    maxWidth: 350,
    canClose: false,
    canResize: true,
  },
  'template-grid': {
    title: 'Templates',
    width: 0, // Takes remaining space
    minWidth: 600,
    canClose: true,
    canResize: false,
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
const CAPACITY_THRESHOLD = 1.2; // Allow 120% of minWidth before retiring (allows some overflow/resizing)

export const usePanelStore = create<PanelStoreState>((set, get) => ({
  panels: [
    // Template sidebar is always visible on the left
    {
      id: 'panel-template-sidebar-0',
      type: 'template-sidebar',
      isVisible: true,
      data: {},
      ...defaultPanelConfig['template-sidebar'],
    } as PanelState,
    // Template grid is the main content area
    {
      id: 'panel-template-grid-0',
      type: 'template-grid',
      isVisible: true,
      data: {},
      ...defaultPanelConfig['template-grid'],
    } as PanelState,
  ],
  retiredPanels: [],
  activePanel: 'panel-template-grid-0',

  openPanel: (type, data = {}, options = {}) => {
    // For template-grid, replace existing one instead of adding new
    if (type === 'template-grid') {
      const existingGrid = get().panels.find(p => p.type === 'template-grid');
      if (existingGrid) {
        set((state) => ({
          panels: state.panels.map(p =>
            p.id === existingGrid.id
              ? { ...p, data: { ...p.data, ...data }, ...options }
              : p
          ),
          activePanel: existingGrid.id,
        }));
        return;
      }
    }

    // For template-detail, replace existing one instead of adding new
    if (type === 'template-detail') {
      const existingDetail = get().panels.find(p => p.type === 'template-detail');
      if (existingDetail) {
        set((state) => ({
          panels: state.panels.map(p =>
            p.id === existingDetail.id
              ? { ...p, data: { ...p.data, ...data }, ...options }
              : p
          ),
          activePanel: existingDetail.id,
        }));
        return;
      }
    }

    // For project-config, replace existing one instead of adding new
    if (type === 'project-config') {
      const existingConfig = get().panels.find(p => p.type === 'project-config');
      if (existingConfig) {
        set((state) => ({
          panels: state.panels.map(p =>
            p.id === existingConfig.id
              ? { ...p, data: { ...p.data, ...data }, ...options }
              : p
          ),
          activePanel: existingConfig.id,
        }));
        return;
      }
    }

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

    // Check capacity and retire panels if needed
    get().checkCapacityAndRetire();
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

  // Carousel navigation methods
  scrollLeft: () => {
    const state = get();
    console.log('[Carousel] scrollLeft called, retiredPanels:', state.retiredPanels.length);

    if (state.retiredPanels.length === 0) {
      console.log('[Carousel] No retired panels to restore');
      return;
    }

    // Restore the most recently retired panel (LIFO - Last In First Out)
    const restoredPanel = state.retiredPanels[state.retiredPanels.length - 1];
    console.log('[Carousel] Restoring panel:', restoredPanel.type, restoredPanel.title);

    const newRetiredPanels = state.retiredPanels.slice(0, -1);

    const visiblePanels = state.panels;

    // Find sidebar index (should always be 0, but let's be safe)
    const sidebarIndex = visiblePanels.findIndex(p => p.type === 'template-sidebar');

    // Calculate total width with restored panel
    const totalMinWidth = visiblePanels.reduce((sum, p) => sum + (p.width || p.minWidth), 0)
                        + (restoredPanel.width || restoredPanel.minWidth);
    const viewportWidth = window.innerWidth;
    const capacityUsed = totalMinWidth / viewportWidth;

    if (capacityUsed > CAPACITY_THRESHOLD && visiblePanels.length > 2) {
      // Need to retire rightmost panel to make room
      const panelToRetire = visiblePanels[visiblePanels.length - 1];
      console.log('[Carousel] Retiring rightmost panel to make room:', panelToRetire.type);

      // Insert restored panel right after sidebar, remove rightmost
      const newPanels = [
        ...visiblePanels.slice(0, sidebarIndex + 1),  // Sidebar
        restoredPanel,                                 // Restored panel
        ...visiblePanels.slice(sidebarIndex + 1, -1)  // Other panels (excluding rightmost)
      ];

      set({
        panels: newPanels,
        retiredPanels: [...newRetiredPanels, panelToRetire],
      });
    } else {
      // Just restore without retiring
      console.log('[Carousel] Restoring panel without retirement');
      const newPanels = [
        ...visiblePanels.slice(0, sidebarIndex + 1),  // Sidebar
        restoredPanel,                                 // Restored panel
        ...visiblePanels.slice(sidebarIndex + 1)      // Other panels
      ];

      set({
        panels: newPanels,
        retiredPanels: newRetiredPanels,
      });
    }
  },

  scrollRight: () => {
    const state = get();
    const visiblePanels = state.panels;
    console.log('[Carousel] scrollRight called, visiblePanels:', visiblePanels.length);

    // Find first panel that can be retired (not sidebar, not the only remaining panel)
    const retirableIndex = visiblePanels.findIndex((p, idx) =>
      p.type !== 'template-sidebar' && idx < visiblePanels.length - 1
    );

    if (retirableIndex === -1) {
      console.log('[Carousel] No retirable panel found');
      return;
    }

    const panelToRetire = visiblePanels[retirableIndex];
    console.log('[Carousel] Retiring panel:', panelToRetire.type, panelToRetire.title);
    const newPanels = visiblePanels.filter((_, idx) => idx !== retirableIndex);

    set({
      panels: newPanels,
      retiredPanels: [...state.retiredPanels, panelToRetire],
    });
  },

  canScrollLeft: () => {
    const retiredCount = get().retiredPanels.length;
    const canScroll = retiredCount > 0;
    console.log('[Carousel] canScrollLeft:', canScroll, `(${retiredCount} retired panels)`);
    return canScroll;
  },

  canScrollRight: () => {
    const visiblePanels = get().panels;
    const canScroll = visiblePanels.length > 2;
    console.log('[Carousel] canScrollRight:', canScroll, `(${visiblePanels.length} visible panels)`);
    // Can scroll right if we have more than 2 panels (sidebar + at least 2 content panels)
    return canScroll;
  },

  checkCapacityAndRetire: () => {
    const state = get();
    const visiblePanels = state.panels;

    // Calculate total minimum width needed
    const totalMinWidth = visiblePanels.reduce((sum, panel) => {
      return sum + (panel.width || panel.minWidth);
    }, 0);

    // Get viewport width
    const viewportWidth = window.innerWidth;
    const capacityUsed = totalMinWidth / viewportWidth;

    console.log('[Carousel] Capacity check:', {
      totalMinWidth,
      viewportWidth,
      capacityUsed: `${(capacityUsed * 100).toFixed(1)}%`,
      threshold: `${(CAPACITY_THRESHOLD * 100).toFixed(0)}%`,
      visiblePanelCount: visiblePanels.length,
      retiredPanelCount: state.retiredPanels.length,
      shouldRetire: capacityUsed > CAPACITY_THRESHOLD
    });

    // If we exceed 75% capacity and have retirable panels
    if (capacityUsed > CAPACITY_THRESHOLD) {
      // Find first panel that can be retired (not sidebar)
      const retirableIndex = visiblePanels.findIndex(p => p.type !== 'template-sidebar');

      if (retirableIndex !== -1 && visiblePanels.length > 2) {
        const panelToRetire = visiblePanels[retirableIndex];
        console.log('[Carousel] Retiring panel:', panelToRetire.type, panelToRetire.title);

        const newPanels = visiblePanels.filter((_, idx) => idx !== retirableIndex);

        set({
          panels: newPanels,
          retiredPanels: [...state.retiredPanels, panelToRetire],
        });
      } else {
        console.log('[Carousel] Cannot retire - no eligible panels or too few panels');
      }
    }
  },
}));
