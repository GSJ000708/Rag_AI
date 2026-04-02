"""文件解析工具"""
import os
from typing import List
from PyPDF2 import PdfReader
from docx import Document
from loguru import logger


class FileParser:
    """文件解析器"""
    
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """
        解析 PDF 文件
        
        Args:
            file_path: PDF 文件路径
            
        Returns:
            提取的文本内容
        """
        try:
            reader = PdfReader(file_path)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            logger.info(f"Parsed PDF: {file_path} ({len(text)} chars)")
            return text.strip()
            
        except Exception as e:
            logger.error(f"PDF parsing error: {e}")
            raise Exception(f"PDF解析失败: {str(e)}")
    
    @staticmethod
    def parse_docx(file_path: str) -> str:
        """
        解析 Word 文件
        
        Args:
            file_path: Word 文件路径
            
        Returns:
            提取的文本内容
        """
        try:
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            
            logger.info(f"Parsed DOCX: {file_path} ({len(text)} chars)")
            return text.strip()
            
        except Exception as e:
            logger.error(f"DOCX parsing error: {e}")
            raise Exception(f"Word文档解析失败: {str(e)}")
    
    @staticmethod
    def parse_txt(file_path: str) -> str:
        """
        解析 TXT 文件
        
        Args:
            file_path: TXT 文件路径
            
        Returns:
            文本内容
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            logger.info(f"Parsed TXT: {file_path} ({len(text)} chars)")
            return text.strip()
            
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    text = f.read()
                return text.strip()
            except Exception as e:
                logger.error(f"TXT parsing error: {e}")
                raise Exception(f"文本文件解析失败: {str(e)}")
        except Exception as e:
            logger.error(f"TXT parsing error: {e}")
            raise Exception(f"文本文件解析失败: {str(e)}")
    
    @staticmethod
    def parse_file(file_path: str) -> str:
        """
        根据文件扩展名自动选择解析器
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取的文本内容
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return FileParser.parse_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return FileParser.parse_docx(file_path)
        elif ext == '.txt':
            return FileParser.parse_txt(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {ext}")


class TextSplitter:
    """文本分块器"""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """
        将长文本分割成小块
        
        Args:
            text: 输入文本
            
        Returns:
            文本块列表
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # 如果不是最后一块，尝试在句子边界处分割
            if end < text_len:
                # 查找最后的句号、问号、感叹号
                for sep in ['。', '！', '？', '.', '!', '?', '\n']:
                    last_sep = chunk.rfind(sep)
                    if last_sep > self.chunk_size * 0.5:  # 至少保留一半内容
                        chunk = chunk[:last_sep + 1]
                        break
            
            chunks.append(chunk.strip())
            start += self.chunk_size - self.chunk_overlap
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return [c for c in chunks if c]  # 过滤空块
