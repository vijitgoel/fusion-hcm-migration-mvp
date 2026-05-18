'use client';

import Link from 'next/link'
import { BarChart3, Upload, Settings, FileText, CheckCircle, List, Users, Icon, icons } from 'lucide-react'

const navItems = [
  { name: 'Dashboard', icon: BarChart3, href: '/' },
  { name: 'Upload Data', icon: Upload, href: '/upload' },
  { name: 'Folder Scan',icon:Upload ,href: '/batch' },
  { name: 'Mapping', icon: FileText, href: '/mapping' },
  { name: 'Validation', icon: CheckCircle, href: '/validation' },
  { name: 'HDL Generator', icon: FileText, href: '/hdl' },
  { name: 'Migration Jobs', icon: List, href: '/jobs' },
  { name: 'Settings', icon: Settings, href: '/settings' },
]

export default function Sidebar() {
  return (
    <div className="w-64 bg-white border-r border-gray-200 h-full flex flex-col">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-900">Fusion Copilot</h2>
      </div>
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.name}>
              <Link
                href={item.href}
                className="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors group">
                <item.icon className="w-5 h-5 mr-3 group-hover:text-blue-600" />
                {item.name}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  )
}