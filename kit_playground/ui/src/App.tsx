import { Header } from './components/layout';
import { PanelContainer, PanelPlaceholder } from './components/layout';
import { TemplateSidebar } from './components/panels/TemplateSidebar';
import { TemplateGrid } from './components/panels/TemplateGrid';
import { TemplateDetail } from './components/panels/TemplateDetail';
import { ProjectConfig } from './components/panels/ProjectConfig';
import { BuildOutput } from './components/panels/BuildOutput';
import { CodeEditor } from './components/panels/CodeEditor';
import { Preview } from './components/panels/Preview';
import { useTemplates } from './hooks/useTemplates';

/**
 * Main App Component
 *
 * Uses a panel-based layout system with:
 * - Compact sidebar (left) for navigation
 * - Main content area (center/right) for templates grid and details
 * - Progressive disclosure of additional panels as needed
 */
function App() {
  // Fetch templates for the grid
  const { templates } = useTemplates();

  /**
   * Render the appropriate component for each panel type
   */
  const renderPanel = (_panelId: string, panelType: string, panelData: any) => {
    switch (panelType) {
      case 'template-sidebar':
        return <TemplateSidebar />;

      case 'template-grid':
        // Use data if provided, otherwise show all templates
        const gridTemplates = panelData?.templates || templates;
        const filterType = panelData?.filterType || 'all';
        return <TemplateGrid templates={gridTemplates} filterType={filterType} />;

      case 'template-detail':
        return panelData?.template
          ? <TemplateDetail template={panelData.template} />
          : <PanelPlaceholder type="template-detail" message="No template selected" />;

      case 'project-detail':
        return <PanelPlaceholder type="project-detail" message="Project detail view coming soon!" />;

      case 'project-config':
        return panelData?.template
          ? <ProjectConfig template={panelData.template} />
          : <PanelPlaceholder type="project-config" message="No template selected" />;

      case 'code-editor':
        return <CodeEditor {...panelData} />;

      case 'build-output':
        return <BuildOutput {...panelData} />;

      case 'preview':
        return <Preview {...panelData} />;

      default:
        return <PanelPlaceholder type={panelType} message={`Unknown panel type: ${panelType}`} />;
    }
  };

  return (
    <div className="app-container flex flex-col w-screen h-screen bg-bg-dark overflow-hidden">
      {/* Header */}
      <Header />

      {/* Panel Container */}
      <div className="flex-1 overflow-hidden">
        <PanelContainer renderPanel={renderPanel} />
      </div>
    </div>
  );
}

export default App;
