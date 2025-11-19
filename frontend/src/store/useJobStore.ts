import { create } from 'zustand'
import type { Job } from '@/types'
import * as api from '@/api/client'

interface JobState {
  jobs: Map<string, Job>
  activeJobId: string | null

  // Actions
  addJob: (job: Job) => void
  updateJob: (jobId: string, updates: Partial<Job>) => void
  getJob: (jobId: string) => Job | undefined
  pollJob: (
    jobId: string,
    onProgress?: (job: Job) => void,
    maxWaitSeconds?: number
  ) => Promise<Job>
  setActiveJob: (jobId: string | null) => void
  clearJobs: () => void
}

export const useJobStore = create<JobState>((set, get) => ({
  jobs: new Map(),
  activeJobId: null,

  addJob: (job: Job) => {
    set((state) => {
      const newJobs = new Map(state.jobs)
      newJobs.set(job.job_id, job)
      return { jobs: newJobs }
    })
  },

  updateJob: (jobId: string, updates: Partial<Job>) => {
    set((state) => {
      const job = state.jobs.get(jobId)
      if (!job) return state

      const newJobs = new Map(state.jobs)
      newJobs.set(jobId, { ...job, ...updates })
      return { jobs: newJobs }
    })
  },

  getJob: (jobId: string) => {
    return get().jobs.get(jobId)
  },

  pollJob: async (
    jobId: string,
    onProgress?: (job: Job) => void,
    maxWaitSeconds: number = 120
  ) => {
    const { updateJob } = get()

    const job = await api.pollJob(
      jobId,
      (updatedJob) => {
        updateJob(jobId, updatedJob)
        if (onProgress) {
          onProgress(updatedJob)
        }
      },
      maxWaitSeconds
    )

    return job
  },

  setActiveJob: (jobId: string | null) => {
    set({ activeJobId: jobId })
  },

  clearJobs: () => {
    set({ jobs: new Map(), activeJobId: null })
  },
}))
