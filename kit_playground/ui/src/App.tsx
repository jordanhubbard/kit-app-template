import { Header } from './components/layout';
import { PanelContainer, PanelPlaceholder } from './components/layout';
import { TemplateBrowser } from './components/panels/TemplateBrowser';
import { TemplateDetail } from './components/panels/TemplateDetail';
import { ProjectConfig } from './components/panels/ProjectConfig';
import { BuildOutput } from './components/panels/BuildOutput';
import { CodeEditor } from './components/panels/CodeEditor';

/**
 * Main App Component
 *
 * Uses a panel-based layout system instead of traditional routing.
 * Panels progressively reveal as the user interacts with the application.
 */
function App() {
  /**
   * Render the appropriate component for each panel type
   */
  const renderPanel = (_panelId: string, panelType: string, panelData: any) => {
    switch (panelType) {
      case 'template-browser':
        return <TemplateBrowser />;

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
        return <PanelPlaceholder type="preview" message="Preview panel coming soon!" />;

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
