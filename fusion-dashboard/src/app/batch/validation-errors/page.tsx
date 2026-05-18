// app/batch/validation-errors/page.tsx
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AlertCircle } from 'lucide-react';

type ValidationSummaryPayload = {
  errors: string[];
  total_files?: number;
  processed_files?: number;
  skipped_files?: number;
  message?: string;
  savedAt?: string;
};

const STORAGE_KEY = 'fusion_batch_validation_summary';

export default function ValidationErrorsPage() {
  const [payload, setPayload] = useState<ValidationSummaryPayload | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setPayload(JSON.parse(raw) as ValidationSummaryPayload);
    } catch {
      setPayload(null);
    }
  }, []);

  const errors = payload?.errors ?? [];

  return (
    <main className="min-h-screen bg-gray-50 p-6 md:p-8">
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Validation Summary Errors</h1>
            <p className="mt-1 text-sm text-gray-600">Detailed error list from the latest batch run.</p>
          </div>
          <Link
            href="/batch"
            className="inline-flex items-center rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Back to scanner
          </Link>
        </div>

        <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          {payload?.message && (
            <div className="mb-4 rounded-xl bg-gray-50 p-4">
              <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-gray-700">Message</h2>
              <p className="text-gray-700">{payload.message}</p>
            </div>
          )}

          {errors.length > 0 ? (
            <ul className="space-y-2">
              {errors.map((message, index) => (
                <li
                  key={`${index}-${message}`}
                  className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
                >
                  <div className="mb-1 flex items-center gap-2 font-medium text-red-800">
                    <AlertCircle className="h-4 w-4" />
                    Error {index + 1}
                  </div>
                  {message}
                </li>
              ))}
            </ul>
          ) : (
            <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-sm text-gray-600">
              No validation summary errors were found, or the details are not available in this browser session.
            </div>
          )}
        </section>
      </div>
    </main>
  );
}