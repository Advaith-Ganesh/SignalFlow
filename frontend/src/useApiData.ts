import { useEffect, useState } from 'react'

interface ApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

/** Fetches once on mount and exposes {data, loading, error}. No caching/retry
 * logic beyond that -- this dashboard reads a small, static research dataset
 * that never changes at runtime. */
export function useApiData<T>(fetcher: () => Promise<T>): ApiState<T> {
  const [state, setState] = useState<ApiState<T>>({ data: null, loading: true, error: null })

  useEffect(() => {
    let cancelled = false
    setState({ data: null, loading: true, error: null })
    fetcher()
      .then((data) => {
        if (!cancelled) setState({ data, loading: false, error: null })
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : 'Unknown error'
          setState({ data: null, loading: false, error: message })
        }
      })
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return state
}
