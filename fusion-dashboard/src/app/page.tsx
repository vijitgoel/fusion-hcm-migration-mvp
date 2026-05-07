'use client';

import KpiCard from '@/components/KpiCard'
import StatusBadge from '@/components/StatusBadge'
import JobTable from '@/components/JobTable'
import { CheckCircle, List, Loader2, AlertCircle, Clock } from 'lucide-react'

const kpis = [
  { title: 'Successful Jobs', value: 127, color: 'bg-green-500' },
  { title: 'Total Jobs', value: 245, color: 'bg-orange-500' },
  { title: 'Running Jobs', value: 3, color: 'bg-blue-500' },
  { title: 'Failed Jobs', value: 8, color: 'bg-red-500' },
  { title: 'Pending Jobs', value: 12, color: 'bg-gray-500' },
]

const jobs = [
  { id: '#MIG-001', file: 'workers.xlsx', type: 'Worker', status: 'SUCCESS', records: 1500, errors: 0, start: '2026-05-01 10:30', },
  { id: '#MIG-002', file: 'assignments.csv', type: 'Assignment', status: 'RUNNING', records: 850, errors: 0, start: '2026-05-02 09:15', },
  { id: '#MIG-003', file: 'salary.xlsx', type: 'Salary', status: 'FAILED', records: 320, errors: 15, start: '2026-05-01 14:20', },
  { id: '#MIG-004', file: 'workers.csv', type: 'Worker', status: 'PENDING', records: 0, errors: 0, start: '2026-05-02 11:00', },
  { id: '#MIG-005', file: 'assignments.xlsx', type: 'Assignment', status: 'SUCCESS', records: 1200, errors: 0, start: '2026-04-30 16:45', },
]

export default function Dashboard() {
  return (
    <main className="flex-1 overflow-y-auto p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Migration Dashboard</h1>
        <p className="text-lg text-gray-600">Monitor and manage HCM data migration jobs</p>
        <div className="flex gap-4 mt-6">
          <select className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500">
            <option>Migration Type</option>
            <option>Worker</option>
            <option>Assignment</option>
            <option>Salary</option>
          </select>
          <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-semibold transition-colors">
            + New Migration
          </button>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        {kpis.map((kpi) => (
          <KpiCard key={kpi.title} {...kpi} />
        ))}
      </div>
      <JobTable />
    </main>
  );
}
