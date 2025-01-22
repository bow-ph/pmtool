import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../api/client';
import { Package } from '../../types/api';

const PackageAdmin = () => {
  const queryClient = useQueryClient();

  const { data: packages, isLoading } = useQuery<Package[]>({
    queryKey: ['packages'],
    queryFn: async () => {
      const response = await apiClient.get('/packages');
      return response.data;
    },
  });

  const updatePackageMutation = useMutation({
    mutationFn: async (updatedPackage: Package) => {
      const response = await apiClient.put(`/packages/${updatedPackage.id}`, updatedPackage);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packages'] });
    },
  });

  const handlePackageUpdate = (pkg: Package) => {
    updatePackageMutation.mutate(pkg);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-2xl font-semibold text-gray-900 mb-6">Paket Verwaltung</h1>
        
        <div className="space-y-6">
          {packages?.map((pkg) => (
            <div key={pkg.id} className="bg-white shadow rounded-lg p-6">
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <input
                    type="text"
                    value={pkg.name}
                    onChange={(e) => handlePackageUpdate({ ...pkg, name: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Preis</label>
                  <input
                    type="number"
                    value={pkg.price}
                    onChange={(e) => handlePackageUpdate({ ...pkg, price: Number(e.target.value) })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Beschreibung</label>
                  <textarea
                    value={pkg.description}
                    onChange={(e) => handlePackageUpdate({ ...pkg, description: e.target.value })}
                    rows={3}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Button Text</label>
                  <input
                    type="text"
                    value={pkg.button_text}
                    onChange={(e) => handlePackageUpdate({ ...pkg, button_text: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>
              </div>

              <div className="mt-6">
                <label className="block text-sm font-medium text-gray-700">Features</label>
                <div className="mt-2 space-y-2">
                  {pkg.features.map((feature, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <input
                        type="text"
                        value={feature}
                        onChange={(e) => {
                          const newFeatures = [...pkg.features];
                          newFeatures[index] = e.target.value;
                          handlePackageUpdate({ ...pkg, features: newFeatures });
                        }}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                      <button
                        onClick={() => {
                          const newFeatures = pkg.features.filter((_, i) => i !== index);
                          handlePackageUpdate({ ...pkg, features: newFeatures });
                        }}
                        className="p-2 text-red-600 hover:text-red-800"
                      >
                        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={() => {
                      handlePackageUpdate({
                        ...pkg,
                        features: [...pkg.features, ''],
                      });
                    }}
                    className="mt-2 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-full text-blue-600 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Feature hinzufügen
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PackageAdmin;
