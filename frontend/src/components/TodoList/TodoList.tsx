// Types
import type { Todo } from '../../types/todo'
// Styles
import './TodoList.css'

interface TodoListProps {
  todos: Todo[]
  onToggle: (id: string) => void
  busyId: string | null
}

const formatDate = (value: string | null): string => {
  if (!value) return '—'
  return new Date(value).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const isOverdue = (todo: Todo): boolean =>
  !todo.completed && todo.dueDate !== null && new Date(todo.dueDate) < new Date()

const TodoList = ({ todos, onToggle, busyId }: TodoListProps) => {
  if (todos.length === 0) {
    return <p className="todo-list__empty">No todos match these filters.</p>
  }

  return (
    <ul className="todo-list">
      {todos.map((todo) => (
        <li
          key={todo.id}
          className={`todo-row${todo.completed ? ' todo-row--done' : ''}`}
        >
          <button
            className={`todo-row__check${todo.completed ? ' todo-row__check--on' : ''}`}
            onClick={() => onToggle(todo.id)}
            disabled={busyId === todo.id}
            aria-label={todo.completed ? 'Mark as active' : 'Mark as completed'}
          >
            {todo.completed ? '✓' : ''}
          </button>

          <div className="todo-row__main">
            <span className="todo-row__title">{todo.title}</span>
            {todo.description && (
              <span className="todo-row__desc">{todo.description}</span>
            )}
          </div>

          <span className={`todo-row__prio todo-row__prio--${todo.priority}`}>
            {todo.priority}
          </span>

          <span
            className={`todo-row__due${isOverdue(todo) ? ' todo-row__due--overdue' : ''}`}
          >
            {formatDate(todo.dueDate)}
          </span>
        </li>
      ))}
    </ul>
  )
}

export default TodoList
