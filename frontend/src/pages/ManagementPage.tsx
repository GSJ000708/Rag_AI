import { useState, useEffect } from 'react';
import { Table, Button, Space, Popconfirm, message, Tag, Card, Statistic, Row, Col, Typography } from 'antd';
import { DeleteOutlined, FileTextOutlined, ReloadOutlined, DatabaseOutlined, FileOutlined, AppstoreOutlined } from '@ant-design/icons';
import { api } from '../services/api';
import type { DocumentInfo } from '../types/api';
import dayjs from 'dayjs';

const { Title } = Typography;

const ManagementPage = () => {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const response = await api.getDocuments();
      setDocuments(response.documents);
      setTotal(response.total);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取文档列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleDelete = async (documentId: string, filename: string) => {
    try {
      await api.deleteDocument(documentId);
      message.success(`文档 "${filename}" 已删除`);
      loadDocuments();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败');
    }
  };

  const columns = [
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
      render: (text: string) => (
        <Space>
          <FileTextOutlined style={{ fontSize: '16px', color: '#667eea' }} />
          <span style={{ fontWeight: 500 }}>{text}</span>
        </Space>
      ),
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (size: number) => (
        <Tag color="blue" style={{ borderRadius: '4px' }}>
          {(size / 1024).toFixed(2)} KB
        </Tag>
      ),
    },
    {
      title: '分块数',
      dataIndex: 'chunks_count',
      key: 'chunks_count',
      render: (count: number) => (
        <Tag 
          color="purple" 
          style={{ 
            borderRadius: '4px',
            fontSize: '13px',
            fontWeight: 500,
          }}
        >
          {count} 块
        </Tag>
      ),
    },
    {
      title: '上传时间',
      dataIndex: 'upload_time',
      key: 'upload_time',
      render: (time: string) => (
        <span style={{ color: '#666' }}>
          {dayjs(time).format('YYYY-MM-DD HH:mm:ss')}
        </span>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_: any, record: DocumentInfo) => (
        <Popconfirm
          title="确认删除"
          description={`确定要删除文档 "${record.filename}" 吗？`}
          onConfirm={() => handleDelete(record.document_id, record.filename)}
          okText="确认"
          cancelText="取消"
          okButtonProps={{
            style: {
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none',
            }
          }}
        >
          <Button type="link" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ];

  const totalSize = documents.reduce((sum, doc) => sum + doc.file_size, 0);
  const totalChunks = documents.reduce((sum, doc) => sum + doc.chunks_count, 0);

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
          📁 知识库管理
        </Title>
        <p style={{ color: '#666', margin: 0, fontSize: '15px' }}>
          查看和管理所有已上传的文档
        </p>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={8}>
          <Card 
            style={{
              borderRadius: '12px',
              border: '1px solid #e5e7eb',
              background: 'linear-gradient(135deg, #667eea 10%, #764ba2 100%)',
            }}
            bodyStyle={{ padding: '24px' }}
          >
            <Statistic
              title={<span style={{ color: 'rgba(255,255,255,0.9)', fontSize: '14px' }}>文档总数</span>}
              value={total}
              suffix="个"
              valueStyle={{ color: '#fff', fontSize: '32px', fontWeight: 'bold' }}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card 
            style={{
              borderRadius: '12px',
              border: '1px solid #e5e7eb',
              background: 'linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 90%)',
            }}
            bodyStyle={{ padding: '24px' }}
          >
            <Statistic
              title={<span style={{ color: 'rgba(255,255,255,0.9)', fontSize: '14px' }}>总存储大小</span>}
              value={(totalSize / 1024).toFixed(2)}
              suffix="KB"
              valueStyle={{ color: '#fff', fontSize: '32px', fontWeight: 'bold' }}
              prefix={<FileOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card 
            style={{
              borderRadius: '12px',
              border: '1px solid #e5e7eb',
              background: 'linear-gradient(135deg, #FFA8A8 0%, #FCFF00 100%)',
            }}
            bodyStyle={{ padding: '24px' }}
          >
            <Statistic
              title={<span style={{ color: 'rgba(0,0,0,0.7)', fontSize: '14px' }}>总分块数</span>}
              value={totalChunks}
              suffix="块"
              valueStyle={{ color: 'rgba(0,0,0,0.85)', fontSize: '32px', fontWeight: 'bold' }}
              prefix={<AppstoreOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 文档列表 */}
      <Card
        title={
          <span style={{ fontSize: '16px', fontWeight: 'bold' }}>
            📄 文档列表
          </span>
        }
        extra={
          <Button 
            icon={<ReloadOutlined />} 
            onClick={loadDocuments}
            style={{
              borderRadius: '6px',
            }}
          >
            刷新
          </Button>
        }
        style={{
          borderRadius: '12px',
          border: '1px solid #e5e7eb',
        }}
      >
        <Table
          columns={columns}
          dataSource={documents}
          rowKey="document_id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => (
              <span style={{ fontWeight: 500 }}>
                共 <span style={{ color: '#667eea' }}>{total}</span> 个文档
              </span>
            ),
          }}
          style={{
            borderRadius: '8px',
          }}
        />
      </Card>
    </div>
  );
};

export default ManagementPage;
