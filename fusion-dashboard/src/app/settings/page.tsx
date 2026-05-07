'use client';

export default function SettingsPage() {
  return (
    <main className="flex-1 overflow-y-auto p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Settings</h1>
        <p className="text-lg text-gray-600 mb-8">Configure your migration settings</p>
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <h2 className="text-2xl font-semibold text-gray-500 mb-4">Coming Soon</h2>
          <p className="text-gray-400">Settings configuration will be available in the next release.</p>
        </div>
      </div>
    </main>
  );
}