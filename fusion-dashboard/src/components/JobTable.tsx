'use client';

import StatusBadge from './StatusBadge';

const mockJobs = [
  { id: '#MIG-001', file: 'workers.xlsx', type: 'Worker', status: 'SUCCESS', records: 1500, errors: 0, start: '2026-05-01 10:30' },
  { id: '#MIG-002', file: 'assignments.csv', type: 'Assignment', status: 'RUNNING', records: 850, errors: 0, start: '2026-05-02 09:15' },
  { id: '#MIG-003', file: 'salary.xlsx', type: 'Salary', status: 'FAILED', records: 320, errors: 15, start: '2026-05-01 14:20' },
  { id: '#MIG-004', file: 'workers.csv', type: 'Worker', status: 'PENDING', records: 0, errors: 0, start: '2026-05-02 11:00' },
  { id: '#MIG-005', file: 'assignments.xlsx', type: 'Assignment', status: 'SUCCESS', records: 1200, errors: 0, start: '2026-04-30 16:45' },
];

export default function JobTable() {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Recent Migration Jobs</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Job ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Records</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Errors</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Started</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {mockJobs.map((job, index) => (
              <tr key={index}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{job.id}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{job.file}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{job.type}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <StatusBadge status={job.status} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{job.records}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{job.errors}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{job.start}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}