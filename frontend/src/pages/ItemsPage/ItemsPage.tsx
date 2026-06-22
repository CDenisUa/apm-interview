// Core
import { useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
// Services
import { useItemsQuery } from '../../gql/generated'
// Types
import type { ItemsQueryVariables } from '../../gql/generated'
import type { Country, ItemStatus } from '../../types/item'
// Styles
import './ItemsPage.css'

const ItemsPage = () => {
  const { t, i18n } = useTranslation()
  const money = useMemo(
    () =>
      new Intl.NumberFormat(i18n.language, {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0,
      }),
    [i18n.language],
  )
  const [search, setSearch] = useState('')
  const [country, setCountry] = useState<Country | ''>('')
  const [status, setStatus] = useState<ItemStatus | ''>('')

  const variables = useMemo<ItemsQueryVariables>(
    () => ({
      search: search || undefined,
      country: country || undefined,
      status: status || undefined,
    }),
    [search, country, status],
  )

  const { data, loading, error } = useItemsQuery({ variables })
  const items = data?.items

  return (
    <div className="items-page">
      <header className="items-page__head">
        <h1 className="items-page__title">{t('items.title')}</h1>
        <p className="items-page__sub">
          {items ? t('items.count', { count: items.length }) : t('items.loading')}
        </p>
      </header>

      <div className="items-page__filters">
        <input
          className="items-page__search"
          placeholder={t('items.searchPlaceholder')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="items-page__select"
          value={country}
          onChange={(e) => setCountry(e.target.value as Country | '')}
        >
          <option value="">{t('items.allCountries')}</option>
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
          <option value="">{t('items.allStatuses')}</option>
          <option value="active">{t('items.status.active')}</option>
          <option value="pending">{t('items.status.pending')}</option>
          <option value="inactive">{t('items.status.inactive')}</option>
        </select>
      </div>

      {error && (
        <p className="items-page__error">{t('items.error', { message: error.message })}</p>
      )}

      {loading && !items ? (
        <p className="items-page__loading">{t('items.loading')}</p>
      ) : (
        items &&
        (items.length === 0 ? (
          <p className="items-page__empty">{t('items.empty')}</p>
        ) : (
          <div className="items-page__table-wrap">
            <table className="items-table">
              <thead>
                <tr>
                  <th>{t('items.table.name')}</th>
                  <th>{t('items.table.country')}</th>
                  <th>{t('items.table.status')}</th>
                  <th className="items-table__num">{t('items.table.revenue')}</th>
                  <th>{t('items.table.owner')}</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td className="items-table__name">{item.name}</td>
                    <td>{item.country}</td>
                    <td>
                      <span className={`items-table__status items-table__status--${item.status}`}>
                        {t(`items.status.${item.status}`)}
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
