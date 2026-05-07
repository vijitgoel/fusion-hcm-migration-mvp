'use client';

type PreviewTableProps = {
  data: Record<string, any>[];
};

export default function PreviewTable({ data }: PreviewTableProps) {
  if (!data || data.length === 0) {
    return (
      <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg text-gray-600">
        No preview data available.
      </div>
    );
  }

  const columns = Object.keys(data[0]);

  return (
    <div className="mt-6 overflow-x-auto bg-white border border-gray-200 rounded-lg shadow-sm">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-100">
          <tr>
            {columns.map((col) => (
              <th
                key={col}
                className="px-4 py-3 text-left font-semibold text-gray-700 border-b border-gray-200"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx} className="hover:bg-gray-50">
              {columns.map((col) => (
                <td
                  key={col}
                  className="px-4 py-3 border-b border-gray-100 text-gray-700"
                >
                  {row[col] === null || row[col] === undefined || row[col] === ""
                    ? "-"
                    : String(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}