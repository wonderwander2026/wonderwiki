#!/usr/bin/env python3
"""
WonderWiki - 记忆维基数据扫描器
扫描 Obsidian vault，生成 index.json 供前端使用。
"""

import os
import re
import json
import yaml
from pathlib import Path
from datetime import datetime, date

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

VAULT = r'C:\Users\wonde\Documents\wondervault'

def parse_frontmatter(content):
    """解析 YAML frontmatter"""
    fm = {}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
            except:
                pass
    return fm

def extract_links(content):
    """提取 [[wiki-links]]"""
    return re.findall(r'\[\[(.+?)\]\]', content)

def extract_tags(fm):
    """提取 tags"""
    tags = fm.get('tags', [])
    if isinstance(tags, str):
        tags = [tags]
    return tags

def classify_by_keywords(content, title, summary=""):
    """基于关键词自动分类"""
    text = (title + " " + content[:2000] + " " + summary).lower()
    
    categories = {
        'ai-agents': ['agent', 'multi-agent', 'agentic', 'autonomous agent', 'agent sdk', 'agent framework'],
        'ai-tools': ['tool', 'sdk', 'framework', 'library', 'cli', 'api', 'platform'],
        'knowledge-mgmt': ['knowledge', 'wiki', 'obsidian', 'notion', 'bookmark', 'personal knowledge', 'pkms'],
        'finance-stocks': ['stock', '股', '财报', 'semiconductor', 'hbm', 'gpu', 'ai chip', '半导体'],
        'entertainment': ['music', 'song', 'movie', 'film', '歌', '电影', '粤'],
        'projects': ['project', 'app', 'web', 'vue', 'react', 'full-stack', 'deploy'],
        'twitter-x': ['x.com', 'twitter', 'tweet', 'threads'],
        'youtube': ['youtube', 'video', '油管', '频道', 'watch?v='],
        'overview': ['overview', '概述', 'summary'],
    }
    
    scores = {}
    for cat, keywords in categories.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[cat] = score
    
    if scores:
        return max(scores, key=scores.get)
    return 'uncategorized'

def scan_vault():
    """扫描整个 vault"""
    files = []
    links = []
    categories = {}
    
    for root, dirs, fnames in os.walk(VAULT):
        # Skip hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for fname in fnames:
            if not fname.endswith('.md'):
                continue
            
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, VAULT)
            
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                continue
            
            if len(content) < 50:
                continue
            
            fm = parse_frontmatter(content)
            title = fm.get('title', fname.replace('.md', ''))
            summary = fm.get('summary', '')
            tags = extract_tags(fm)
            wiki_links = extract_links(content)
            created = fm.get('created', '')
            clipped = fm.get('clipped', '')
            source = fm.get('source', '')
            date_str = created or clipped
            
            # 提取正文内容（去除 frontmatter）
            body_content = content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    body_content = parts[2]
            
            # Determine category from path
            parts = rel_path.split(os.sep)
            if len(parts) >= 2:
                if parts[0] == 'raw':
                    # Skip 'Clippings' subdirectory — it's a staging area, not a category
                    # For raw/Clippings/ai-agents/xxx.md → category = 'ai-agents'
                    # For raw/Clippings/xxx.md (no sub) → auto-classify
                    # For raw/ai-agents/xxx.md → category = 'ai-agents'
                    remaining = parts[1:]
                    if remaining[0] == 'Clippings':
                        remaining = remaining[1:]  # skip Clippings
                    if len(remaining) >= 2:
                        category = remaining[0]
                    else:
                        category = 'raw-root'
                elif parts[0] == 'wiki':
                    if parts[1] == 'concepts':
                        category = 'wiki/concepts'
                    elif parts[1] == 'entities':
                        category = 'wiki/entities'
                    elif parts[1] == 'sources':
                        category = 'wiki/sources'
                    elif parts[1] == 'schema':
                        category = 'wiki/schema'
                    else:
                        category = parts[1]
                elif parts[0] == 'Clippings':
                    # Root-level Clippings — needs classification
                    category = 'Clippings'
                else:
                    category = 'root'
            else:
                category = 'root'
            
            # Auto-classify if no good category
            if category in ('raw-root', 'root'):
                category = classify_by_keywords(body_content, title, summary)
            
            # Track links
            for link in wiki_links:
                links.append({
                    'from': rel_path,
                    'to': link
                })
            
            # Track category counts
            categories[category] = categories.get(category, 0) + 1
            
            files.append({
                'path': rel_path,
                'title': title,
                'summary': summary[:300] if summary else '',
                'tags': tags,
                'category': category,
                'date': date_str,
                'source': source,
                'word_count': len(content),
                'links_to': wiki_links[:10],
                'body_preview': body_content[:2000],
                'body_full': body_content,
                '_id': f'f{len(files)}',
            })
    
    return {
        'files': files,
        'links': links,
        'categories': categories,
        'meta': {
            'total_files': len(files),
            'total_links': len(links),
            'scan_date': datetime.now().isoformat(),
            'vault_path': VAULT,
        }
    }

if __name__ == '__main__':
    print("Scanning vault...")
    data = scan_vault()
    
    output_path = r'C:\Users\wonde\studyweb\wonderwiki\data\index.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, cls=DateEncoder)
    
    print(f"Done! {data['meta']['total_files']} files, {data['meta']['total_links']} links")
    print(f"Categories: {json.dumps(data['categories'], ensure_ascii=False, indent=2)}")
    print(f"Output: {output_path}")
