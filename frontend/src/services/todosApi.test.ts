// Core
import { beforeEach, describe, expect, it, vi } from 'vitest'
// Services
import { createTodo, getTodos, toggleTodo } from './todosApi'

const stubFetch = (data: unknown, ok = true, status = 200) => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok,
    status,
    statusText: ok ? 'OK' : 'Error',
    json: () => Promise.resolve(data),
  } as Response)
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

beforeEach(() => {
  vi.unstubAllGlobals()
})

describe('todosApi', () => {
  it('getTodos requests /api/todos with mapped query params', async () => {
    const fetchMock = stubFetch({ items: [], total: 0, page: 2, pageSize: 10, totalPages: 0 })
    await getTodos({ page: 2, pageSize: 10, search: 'foo', priority: 'high' })

    const url = fetchMock.mock.calls[0][0] as string
    expect(url).toContain('/api/todos?')
    expect(url).toContain('page=2')
    expect(url).toContain('page_size=10')
    expect(url).toContain('search=foo')
    expect(url).toContain('priority=high')
  })

  it('createTodo POSTs the payload with defaults applied', async () => {
    const fetchMock = stubFetch({ id: '1' })
    await createTodo({ title: 'New task', priority: 'low' })

    const init = fetchMock.mock.calls[0][1] as RequestInit
    expect(init.method).toBe('POST')
    expect(JSON.parse(init.body as string)).toMatchObject({
      title: 'New task',
      priority: 'low',
      description: '',
      dueDate: null,
    })
  })

  it('toggleTodo POSTs to the toggle endpoint', async () => {
    const fetchMock = stubFetch({ id: 'abc', completed: true })
    await toggleTodo('abc')
    expect(fetchMock.mock.calls[0][0]).toContain('/api/todos/abc/toggle')
  })

  it('throws on a non-ok response', async () => {
    stubFetch(null, false, 500)
    await expect(getTodos({ page: 1, pageSize: 10 })).rejects.toThrow(/500/)
  })
})
