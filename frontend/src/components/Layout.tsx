import { FC, ReactNode } from 'react';
import { Layout as AntLayout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  MessageOutlined,
  UploadOutlined,
  FolderOutlined,
  RobotOutlined,
} from '@ant-design/icons';

const { Header, Content, Footer } = AntLayout;

interface LayoutProps {
  children: ReactNode;
}

const Layout: FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/chat',
      icon: <MessageOutlined />,
      label: '智能问答',
    },
    {
      key: '/upload',
      icon: <UploadOutlined />,
      label: '上传文档',
    },
    {
      key: '/management',
      icon: <FolderOutlined />,
      label: '知识库管理',
    },
  ];

  return (
    <AntLayout style={{ minHeight: '100vh', background: 'transparent' }}>
      <Header 
        style={{ 
          display: 'flex', 
          alignItems: 'center', 
          background: 'rgba(0, 21, 41, 0.95)',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
          position: 'sticky',
          top: 0,
          zIndex: 1000,
        }}
      >
        <div style={{ 
          color: 'white', 
          fontSize: '20px', 
          fontWeight: 'bold',
          marginRight: '50px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}>
          <RobotOutlined style={{ fontSize: '28px', color: '#667eea' }} />
          <span style={{ color: 'white', WebkitTextFillColor: 'white' }}>RAG 知识库助手</span>
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ 
            flex: 1, 
            minWidth: 0,
            background: 'transparent',
            borderBottom: 'none',
          }}
        />
      </Header>
      <Content style={{ 
        padding: '24px',
        background: 'transparent',
      }}>
        <div style={{ 
          background: '#fff', 
          padding: '32px', 
          minHeight: 'calc(100vh - 134px)',
          borderRadius: '16px',
          boxShadow: '0 4px 24px rgba(0,0,0,0.1)',
          animation: 'fadeInUp 0.5s ease-out',
        }}>
          {children}
        </div>
      </Content>
      <Footer style={{ 
        textAlign: 'center', 
        background: 'transparent',
        color: 'white',
        fontWeight: 500,
      }}>
        RAG Knowledge Assistant ©2024 - 基于智谱AI的企业知识库问答系统
      </Footer>
    </AntLayout>
  );
};

export default Layout;
