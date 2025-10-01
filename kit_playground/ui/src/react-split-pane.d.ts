declare module 'react-split-pane' {
  import * as React from 'react';

  export interface SplitPaneProps {
    split?: 'vertical' | 'horizontal';
    minSize?: number | string;
    maxSize?: number | string;
    defaultSize?: number | string;
    size?: number | string;
    primary?: 'first' | 'second';
    onChange?: (newSize: number) => void;
    onDragStarted?: () => void;
    onDragFinished?: (newSize: number) => void;
    allowResize?: boolean;
    className?: string;
    style?: React.CSSProperties;
    resizerStyle?: React.CSSProperties;
    resizerClassName?: string;
    paneClassName?: string;
    pane1ClassName?: string;
    pane2ClassName?: string;
    paneStyle?: React.CSSProperties;
    pane1Style?: React.CSSProperties;
    pane2Style?: React.CSSProperties;
    step?: number;
    children?: React.ReactNode;
  }

  export default class SplitPane extends React.Component<SplitPaneProps> {}
}
