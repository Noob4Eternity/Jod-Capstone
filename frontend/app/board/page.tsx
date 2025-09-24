'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function BoardPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to a default project board or show project selection
    // For now, redirect to a placeholder project
    router.replace('/board/default-project');
  }, [router]);

  return (
    <div className="h-screen bg-gray-100 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading project board...</p>
      </div>
    </div>
  );
}
