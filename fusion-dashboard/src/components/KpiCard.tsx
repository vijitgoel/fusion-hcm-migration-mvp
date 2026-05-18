'use client';

import React from 'react';

interface KpiCardProps {
  title: string;
  value: number;
  color: string;
}

const KpiCard: React.FC<KpiCardProps> = ({ title, value, color }) => {
  return (
    <div className={`p-4 rounded-xl shadow-md ${color}`}>
      <h3 className="text-sm text-gray-500">{title}</h3>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
};

export default KpiCard;