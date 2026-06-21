// Core
import { useMemo, useState } from 'react'
// Hooks
import { useItems } from '../../hooks/useItems/useItems'
// Services
import type { ItemsQuery } from '../../services/itemsApi'
// Types
import type { Country, ItemStatus } from '../../types/item'
// Styles
import './ItemsPage.css'

const money = new Intl.NumberFormat(undefined, {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
})

const ItemsPage = () => {
  const [search, setSearch] = useState('')
  const [country, setCountry] = useState<Country | ''>('')
  const [status, setStatus] = useState<ItemStatus | ''>('')

  const query = useMemo<ItemsQuery>(
    () => ({
      search: search || undefined,
      country: country || undefined,
      status: status || undefined,
    }),
    [search, country, status],
  )

  const { data, loading, error } = useItems(query)

  return (
    <div className="items-page">
      <header className="items-page__head">
        <h1 className="items-page__title">Business Items</h1>
        <p className="items-page__sub">
          {data ? `${data.length} item${data.length === 1 ? '' : 's'}` : 'Loading…'}
        </p>
      </header>

      <div className="items-page__filters">
        <input
          className="items-page__search"
          placeholder="Search by name…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="items-page__select"
          value={country}
          onChange={(e) => setCountry(e.target.value as Country | '')}
        >
          <option value="">All countries</option>
          <option value="AT">AT</option>
          <option value="DE">DE</option>
          <option value="US">US</option>
          <option value="UA">UA</option>
        </select>
        <select
          className="items-page__select"
          value={status}
          onChange={(e) => setStatus(e.target.value as ItemStatus | '')}
        >
          <option value="">All statuses</option>
          <option value="active">Active</option>
          <option value="pending">Pending</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      {error && <p className="items-page__error">Couldn’t load items: {error}</p>}

      {loading && !data ? (
        <p className="items-page__loading">Loading…</p>
      ) : (
        data &&
        (data.length === 0 ? (
          <p className="items-page__empty">No items match these filters.</p>
        ) : (
          <div className="items-page__table-wrap">
            <table className="items-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Country</th>
                  <th>Status</th>
                  <th className="items-table__num">Revenue</th>
                  <th>Owner</th>
                </tr>
              </thead>
              <tbody>
                {data.map((item) => (
                  <tr key={item.id}>
                    <td className="items-table__name">{item.name}</td>
                    <td>{item.country}</td>
                    <td>
                      <span className={`items-table__status items-table__status--${item.status}`}>
                        {item.status}
                      </span>
                    </td>
                    <td className="items-table__num">{money.format(item.revenue)}</td>
                    <td className="items-table__owner">{item.owner}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))
      )}
    </div>
  )
}

export default ItemsPage
