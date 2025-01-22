import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { Package } from '../types/api';
import PackageCard from '../components/Packages/PackageCard';

const PackageSelection = () => {
  const [selectedPackage, setSelectedPackage] = useState<number | null>(null);

  const { data: packages, isLoading } = useQuery<Package[]>({
    queryKey: ['packages'],
    queryFn: async () => {
      const response = await apiClient.get('/packages');
      return response.data;
    },
  });

  const handlePackageSelect = (packageId: number) => {
    setSelectedPackage(packageId);
    // TODO: Implement package selection logic with Mollie integration
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div className="text-center">
        <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
          Wählen Sie Ihr Paket
        </h2>
        <p className="mt-4 text-lg text-gray-500">
          Wählen Sie das passende Paket für Ihre Bedürfnisse
        </p>
      </div>

      <div className="mt-12 grid gap-8 lg:grid-cols-3">
        {packages?.map((pkg) => (
          <PackageCard
            key={pkg.id}
            package={pkg}
            isSelected={selectedPackage === pkg.id}
            onSelect={() => handlePackageSelect(pkg.id)}
          />
        ))}
      </div>

      {selectedPackage && (
        <div className="mt-8 text-center">
          <button
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            onClick={() => {
              // TODO: Implement checkout process
            }}
          >
            Weiter zur Zahlung
          </button>
        </div>
      )}
    </div>
  );
};

export default PackageSelection;
