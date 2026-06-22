// Core
import { useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
// Components
import TodoList from '../../components/TodoList/TodoList'
// Hooks
import { useAuth } from '../../hooks/useAuth/useAuth'
import { useTodos } from '../../hooks/useTodos/useTodos'
// Services
import { toggleTodo } from '../../services/todosApi'
// Types
import type { Priority, TodoQuery } from '../../types/todo'
// Styles
import './TodosPage.css'

const PAGE_SIZE = 10
type StatusFilter = 'all' | 'active' | 'completed'

const TodosPage = () => {
  const { t } = useTranslation()
  const { user } = useAuth()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [debounced, setDebounced] = useState('')
  const [status, setStatus] = useState<StatusFilter>('all')
  const [priority, setPriority] = useState<Priority | ''>('')
  const [busyId, setBusyId] = useState<string | null>(null)

  // Debounce the search box; reset to the first page on a new term.
  useEffect(() => {
    const t = setTimeout(() => {
      setDebounced(search)
      setPage(1)
    }, 300)
    return () => clearTimeout(t)
  }, [search])

  const query = useMemo<TodoQuery>(
    () => ({
      page,
      pageSize: PAGE_SIZE,
      search: debounced || undefined,
      completed: status === 'all' ? undefined : status === 'completed',
      priority: priority || undefined,
      sortBy: 'createdAt',
      order: 'desc',
    }),
    [page, debounced, status, priority],
  )

  const { data, loading, error, refetch } = useTodos(query)

  const handleToggle = async (id: string) => {
    setBusyId(id)
    try {
      await toggleTodo(id)
      refetch()
    } catch {
      /* keep the current view; a transient failure is non-fatal */
    } finally {
      setBusyId(null)
    }
  }

  const totalPages = data?.totalPages ?? 0

  return (
    <div className="todos-page">
      <header className="todos-page__head">
        <div>
          <h1 className="todos-page__title">{t('todos.title')}</h1>
          <p className="todos-page__sub">
            {user ? t('todos.welcomeBack', { name: user.name }) : ''}
            {data
              ? t('todos.count', { count: data.total })
              : t('todos.loading')}
          </p>
        </div>
      </header>

      <div className="todos-page__filters">
        <input
          className="todos-page__search"
          placeholder={t('todos.searchPlaceholder')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="todos-page__segment">
          {(['all', 'active', 'completed'] as StatusFilter[]).map((s) => (
            <button
              key={s}
              className={`todos-page__seg${status === s ? ' todos-page__seg--on' : ''}`}
              onClick={() => {
                setStatus(s)
                setPage(1)
              }}
            >
              {t(`todos.status.${s}`)}
            </button>
          ))}
        </div>
        <select
          className="todos-page__select"
          value={priority}
          onChange={(e) => {
            setPriority(e.target.value as Priority | '')
            setPage(1)
          }}
        >
          <option value="">{t('todos.priority.all')}</option>
          <option value="high">{t('todos.priority.high')}</option>
          <option value="medium">{t('todos.priority.medium')}</option>
          <option value="low">{t('todos.priority.low')}</option>
        </select>
      </div>

      {error && (
        <p className="todos-page__error">{t('todos.error', { message: error })}</p>
      )}

      {loading && !data ? (
        <p className="todos-page__loading">{t('todos.loading')}</p>
      ) : (
        data && (
          <>
            <TodoList todos={data.items} onToggle={handleToggle} busyId={busyId} />
            <div className="todos-page__pager">
              <button
                className="todos-page__pgbtn"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                {t('todos.prev')}
              </button>
              <span className="todos-page__pginfo">
                {t('todos.pageInfo', {
                  page: data.page,
                  total: Math.max(totalPages, 1),
                })}
              </span>
              <button
                className="todos-page__pgbtn"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                {t('todos.next')}
              </button>
            </div>
          </>
        )
      )}
    </div>
  )
}

export default TodosPage
