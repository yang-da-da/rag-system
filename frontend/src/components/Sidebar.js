import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Target, 
  FileText, 
  SpellCheck, 
  Type, 
  PenTool,
  Settings,
  BarChart3
} from 'lucide-react';

const Sidebar = ({ width }) => {
  const location = useLocation();

  const menuItems = [
    { path: '/', icon: Home, label: '首页', description: '系统概览' },
    { path: '/ner', icon: Target, label: '实体识别', description: '识别金融实体' },
    { path: '/stand', icon: FileText, label: '术语标准化', description: '标准化金融术语' },
    { path: '/corr', icon: SpellCheck, label: '拼写纠正', description: '纠正拼写错误' },
    { path: '/abbr', icon: Type, label: '缩写扩展', description: '扩展金融缩写' },
    { path: '/gen', icon: PenTool, label: '文本生成', description: '生成金融文本' },
  ];

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div 
      className="bg-white shadow-lg border-r border-gray-200 flex flex-col"
      style={{ width: `${width}px` }}
    >
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <BarChart3 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">金融RAG系统</h1>
            <p className="text-sm text-gray-500">专有名词标准化</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`group flex items-center space-x-3 px-3 py-3 rounded-lg transition-all duration-200 ${
                active
                  ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Icon 
                className={`w-5 h-5 ${
                  active ? 'text-blue-700' : 'text-gray-400 group-hover:text-gray-600'
                }`} 
              />
              <div className="flex-1">
                <div className={`font-medium ${
                  active ? 'text-blue-700' : 'text-gray-900'
                }`}>
                  {item.label}
                </div>
                <div className={`text-xs ${
                  active ? 'text-blue-600' : 'text-gray-500'
                }`}>
                  {item.description}
                </div>
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center space-x-3 px-3 py-2 text-gray-500 hover:text-gray-700 cursor-pointer transition-colors">
          <Settings className="w-4 h-4" />
          <span className="text-sm">系统设置</span>
        </div>
        <div className="px-3 py-1">
          <div className="text-xs text-gray-400">
            版本 1.0.0
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
