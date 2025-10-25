import { Header } from './components/layout';
import { PanelContainer, PanelPlaceholder } from './components/layout';
import { TemplateBrowser } from './components/panels/TemplateBrowser';

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
  const renderPanel = (_panelId: string, panelType: string, _panelData: any) => {
    switch (panelType) {
      case 'template-browser':
        return <TemplateBrowser />;
      
      case 'template-detail':
        return <PanelPlaceholder type="template-detail" message="Template detail view coming soon!" />;
      
      case 'project-detail':
        return <PanelPlaceholder type="project-detail" message="Project detail view coming soon!" />;
      
      case 'project-config':
        return <PanelPlaceholder type="project-config" message="Project configuration coming soon!" />;
      
      case 'code-editor':
        return <PanelPlaceholder type="code-editor" message="Code editor coming soon!" />;
      
      case 'build-output':
        return <PanelPlaceholder type="build-output" message="Build output view coming soon!" />;
      
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
