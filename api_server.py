#!/usr/bin/env python3
"""
WonderWiki API 服务器
提供文件移动、搜索等后端功能
"""

import os
import json
import shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

VAULT = r'C:\Users\wonde\Documents\wondervault'  # <-- 改成你自己的 Obsidian vault 路径
DATA_DIR = r'C:\Users\wonde\studyweb\wonderwiki\data'  # <-- 改成 data/ 目录的绝对路径
INDEX_JSON = os.path.join(DATA_DIR, 'index.json')

class WonderWikiHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress default logging
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if parsed.path == '/api/files':
            # 获取文件列表和链接数据
            idx = self.load_index()
            self.send_json({
                'files': idx.get('files', []),
                'links': idx.get('links', []),
                'categories': idx.get('categories', {}),
                'meta': idx.get('meta', {})
            })
        elif parsed.path == '/api/categories':
            # 获取分类统计
            data = self.load_index()
            self.send_json({
                'categories': data.get('categories', {}),
                'meta': data.get('meta', {})
            })
        elif parsed.path == '/api/search':
            # 搜索文件
            query = params.get('q', [''])[0]
            if query:
                results = self.search_files(query)
                self.send_json({'results': results, 'count': len(results)})
            else:
                self.send_json({'results': [], 'count': 0})
        elif parsed.path == '/api/links':
            # 获取链接数据
            data = self.load_index()
            self.send_json({'links': data.get('links', [])})
        elif parsed.path == '/api/open':
            # 打开文件
            params = parse_qs(parsed.query)
            file_path = params.get('path', [''])[0]
            if not file_path:
                self.send_json({'error': 'No path provided'}, 400)
                return
            
            import subprocess
            try:
                # 用引号包裹路径，处理空格和特殊字符
                subprocess.Popen(f'explorer /select,"{file_path}"', shell=True)
                self.send_json({'message': f'已打开文件: {file_path}'})
            except Exception as e:
                self.send_json({'error': str(e)}, 500)
            return
        else:
            self.send_json({'error': 'Not found'}, 404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/move':
            # 移动文件到指定分类
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            source_path = data.get('source_path')
            target_category = data.get('target_category')
            
            if not source_path or not target_category:
                self.send_json({'success': False, 'error': '缺少参数'}, 400)
                return
            
            result = self.move_file(source_path, target_category)
            self.send_json(result)
        else:
            self.send_json({'error': 'Not found'}, 404)
    
    def load_index(self):
        try:
            with open(INDEX_JSON, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'files': [], 'links': [], 'categories': {}, 'meta': {}}
    
    def search_files(self, query):
        data = self.load_index()
        query_lower = query.lower()
        results = []
        
        for file_info in data.get('files', []):
            score = 0
            title_lower = file_info.get('title', '').lower()
            summary_lower = file_info.get('summary', '').lower()
            tags = file_info.get('tags', [])
            body = file_info.get('body_preview', '').lower()
            
            # 标题匹配（权重最高）
            if query_lower in title_lower:
                score += 10
            # 正文匹配
            if query_lower in body:
                score += 8
            # 摘要匹配
            if query_lower in summary_lower:
                score += 5
            # 标签匹配
            if any(query_lower in tag.lower() for tag in tags):
                score += 3
            
            if score > 0:
                results.append({
                    'file': file_info,
                    'score': score
                })
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def move_file(self, source_path, target_category):
        """移动文件到目标分类"""
        try:
            full_source = os.path.join(VAULT, source_path)
            
            if not os.path.exists(full_source):
                return {'success': False, 'error': '文件不存在'}
            
            # 确定目标目录
            if source_path.startswith('raw/'):
                parts = source_path.split('/')
                if len(parts) > 2:
                    filename = parts[-1]
                    target_dir = os.path.join(VAULT, 'raw', target_category)
                else:
                    return {'success': False, 'error': '无效的路径'}
            else:
                return {'success': False, 'error': '只能移动 raw/ 下的文件'}
            
            # 创建目标目录（如果不存在）
            os.makedirs(target_dir, exist_ok=True)
            
            # 移动文件
            filename = os.path.basename(full_source)
            target_path = os.path.join(target_dir, filename)
            
            shutil.move(full_source, target_path)
            
            # 更新 index.json
            self.update_category_in_index(source_path, target_category)
            
            return {
                'success': True,
                'message': f'文件已移动到 {target_category}',
                'source': source_path,
                'target': f'raw/{target_category}/{filename}'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_category_in_index(self, old_path, new_category):
        """更新 index.json 中的分类信息"""
        try:
            if os.path.exists(INDEX_JSON):
                with open(INDEX_JSON, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 更新文件分类
                for file_info in data.get('files', []):
                    if file_info.get('path') == old_path:
                        file_info['category'] = new_category
                        break
                
                # 重新计算分类计数
                categories = {}
                for file_info in data.get('files', []):
                    cat = file_info.get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                data['categories'] = categories
                
                with open(INDEX_JSON, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"更新 index.json 失败: {e}")

if __name__ == '__main__':
    server = HTTPServer(('localhost', 19998), WonderWikiHandler)
    print("WonderWiki API 服务器运行在 http://localhost:19998")
    server.serve_forever()
