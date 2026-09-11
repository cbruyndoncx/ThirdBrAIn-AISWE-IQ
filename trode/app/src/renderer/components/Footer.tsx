interface FooterProps {
  lastUpdated: number; // seconds ago
  onRefresh: () => void;
  onSettings: () => void;
  onQuit: () => void;
}

export function Footer({ lastUpdated, onRefresh, onSettings, onQuit }: FooterProps) {
  const formatLastUpdated = (seconds: number): string => {
    if (seconds < 60) {
      return `${seconds} sec ago`;
    }
    const minutes = Math.floor(seconds / 60);
    return `${minutes} min ago`;
  };

  return (
    <footer className="footer">
      <div className="footer-status">
        <span className="last-updated">Updated {formatLastUpdated(lastUpdated)}</span>
        <button className="refresh-btn" onClick={onRefresh} title="Refresh">
          &#x21BB;
        </button>
      </div>
      <div className="footer-actions">
        <button className="footer-btn" onClick={onSettings}>
          Settings
        </button>
        <button className="footer-btn quit-btn" onClick={onQuit}>
          Quit
        </button>
      </div>
    </footer>
  );
}
