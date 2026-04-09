import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import ChatPage from './pages/ChatPage';
import FreeChatPage from './pages/FreeChatPage';
import UploadPage from './pages/UploadPage';
import ManagementPage from './pages/ManagementPage';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/chat" replace />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/freechat" element={<FreeChatPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/management" element={<ManagementPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
