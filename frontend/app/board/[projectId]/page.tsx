'use client';

import { KanbanBoard } from '@/components/KanbanBoard';
import { useParams } from 'next/navigation';

export default function BoardPage() {
  const params = useParams();
  const projectId = params.projectId as string;

  return <KanbanBoard projectId={projectId} />;
}