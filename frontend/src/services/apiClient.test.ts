// Core
import { describe, expect, it } from 'vitest'
// Services
import { toQuery } from './apiClient'

describe('toQuery', () => {
  it('builds a query string and skips empty/undefined/null values', () => {
    expect(
      toQuery({ page: 1, search: '', country: undefined, status: null, q: 'x' }),
    ).toBe('?page=1&q=x')
  })

  it('returns an empty string when there is nothing to add', () => {
    expect(toQuery({ a: undefined, b: '', c: null })).toBe('')
  })

  it('stringifies booleans and numbers', () => {
    expect(toQuery({ completed: false, page: 2 })).toBe('?completed=false&page=2')
  })
})
