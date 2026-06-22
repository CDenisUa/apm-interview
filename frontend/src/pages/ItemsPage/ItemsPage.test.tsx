// Core
import { MockedProvider } from '@apollo/client/testing'
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
// Components
import ItemsPage from './ItemsPage'
// Services
import { ItemsDocument } from '../../gql/generated'

const mocks = [
  {
    request: {
      query: ItemsDocument,
      variables: { search: undefined, country: undefined, status: undefined },
    },
    result: {
      data: {
        items: [
          {
            id: '1',
            name: 'Vienna Logistics Hub',
            country: 'AT',
            status: 'active',
            revenue: 1250000,
            owner: 'a.huber',
            updatedAt: '',
          },
        ],
      },
    },
  },
]

describe('ItemsPage', () => {
  it('renders items returned by the GraphQL query', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <ItemsPage />
      </MockedProvider>,
    )
    expect(await screen.findByText('Vienna Logistics Hub')).toBeInTheDocument()
    expect(screen.getByText(/1 item/i)).toBeInTheDocument()
  })
})
