import { useState } from 'react';
import { Upload, Card, message, Progress, Space, Typography, Alert, Row, Col } from 'antd';
import { InboxOutlined, FileTextOutlined, FilePdfOutlined, FileWordOutlined, CloudUploadOutlined, CheckCircleOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { api } from '../services/api';

const { Dragger } = Upload;
const { Title, Text } = Typography;

const UploadPage = () => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: '.pdf,.docx,.doc,.txt',
    showUploadList: false,
    beforeUpload: (file) => {
      const isValidType = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'text/plain'].includes(file.type);
      
      if (!isValidType) {
        message.error('只支持 PDF、Word 和 TXT 文件！');
        return false;
      }

      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('文件大小不能超过 10MB！');
        return false;
      }

      handleUpload(file);
      return false;
    },
  };

  const handleUpload = async (file: File) => {
    setUploading(true);
    setProgress(0);

    try {
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(interval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      const response = await api.uploadDocument(file);

      clearInterval(interval);
      setProgress(100);

      message.success({
        content: '文档上传成功！',
        icon: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
      });
      
      setUploadedFiles((prev) => [
        ...prev,
        {
          name: response.filename,
          id: response.document_id,
          size: response.file_size,
          chunks: response.chunks_count,
        },
      ]);

      setTimeout(() => {
        setProgress(0);
        setUploading(false);
      }, 1000);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '上传失败，请稍后重试');
      setProgress(0);
      setUploading(false);
    }
  };

  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return <FilePdfOutlined style={{ fontSize: '32px', color: '#ff4d4f' }} />;
    if (ext === 'docx' || ext === 'doc') return <FileWordOutlined style={{ fontSize: '32px', color: '#1890ff' }} />;
    return <FileTextOutlined style={{ fontSize: '32px', color: '#52c41a' }} />;
  };

  return (
    <div>
      {/* 标题 */}
      <div style={{ marginBottom: '32px' }}>
        <Title level={1} style={{ 
          fontSize: '28px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          marginBottom: '8px',
        }}>
          📤 上传文档
        </Title>
        <Text type="secondary" style={{ fontSize: '15px' }}>
          支持 PDF、Word、TXT 格式文档，单个文件不超过 10MB
        </Text>
      </div>

      {/* 上传区域 */}
      <Card 
        style={{ 
          marginBottom: '24px',
          borderRadius: '12px',
          border: '2px dashed #d9d9d9',
          background: 'linear-gradient(to bottom, #fafafa, #ffffff)',
        }}
        bodyStyle={{ padding: '32px' }}
      >
        <Dragger 
          {...uploadProps} 
          disabled={uploading}
          style={{
            background: 'transparent',
            border: 'none',
          }}
        >
          <p className="ant-upload-drag-icon">
            <CloudUploadOutlined style={{ 
              fontSize: '64px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }} />
          </p>
          <p className="ant-upload-text" style={{ fontSize: '18px', fontWeight: 500 }}>
            点击或拖拽文件到此区域上传
          </p>
          <p className="ant-upload-hint" style={{ fontSize: '14px', color: '#999' }}>
            支持 PDF、Word (.docx, .doc)、TXT 格式，单个文件最大 10MB
          </p>
        </Dragger>

        {uploading && (
          <div style={{ marginTop: '24px' }}>
            <Progress 
              percent={progress} 
              status="active"
              strokeColor={{
                '0%': '#667eea',
                '100%': '#764ba2',
              }}
            />
            <Text type="secondary" style={{ 
              display: 'block', 
              textAlign: 'center', 
              marginTop: '12px',
              fontSize: '14px',
            }}>
              正在处理文档，请稍候...
            </Text>
          </div>
        )}
      </Card>

      {/* 已上传文档 */}
      {uploadedFiles.length > 0 && (
        <Card 
          title={
            <span style={{ fontSize: '16px', fontWeight: 'bold' }}>
              📋 本次上传的文档
            </span>
          }
          style={{ 
            marginBottom: '24px',
            borderRadius: '12px',
            border: '1px solid #e5e7eb',
          }}
        >
          <Row gutter={[16, 16]}>
            {uploadedFiles.map((file, index) => (
              <Col span={24} key={index}>
                <Card 
                  size="small"
                  style={{
                    background: 'linear-gradient(to right, #f9fafb, #ffffff)',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                  }}
                >
                  <Space size="large">
                    {getFileIcon(file.name)}
                    <div>
                      <div style={{ fontSize: '15px', fontWeight: 500, marginBottom: '4px' }}>
                        {file.name}
                      </div>
                      <Space split="|">
                        <Text type="secondary" style={{ fontSize: '13px' }}>
                          大小: {(file.size / 1024).toFixed(2)} KB
                        </Text>
                        <Text type="secondary" style={{ fontSize: '13px' }}>
                          分块: {file.chunks} 块
                        </Text>
                      </Space>
                    </div>
                  </Space>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* 使用提示 */}
      <Alert
        message={<span style={{ fontWeight: 500 }}>💡 使用提示</span>}
        description={
          <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.8' }}>
            <li>上传的文档会被自动解析并向量化存储到知识库</li>
            <li>文档会被分割成小块（约 800 字符/块），以提高检索精度</li>
            <li>上传完成后即可在"智能问答"中提问相关问题</li>
            <li>可在"知识库管理"中查看和管理已上传的文档</li>
          </ul>
        }
        type="info"
        showIcon
        style={{ 
          borderRadius: '12px',
          border: '1px solid #91d5ff',
          background: 'linear-gradient(to right, #e6f7ff, #ffffff)',
        }}
      />
    </div>
  );
};

export default UploadPage;
