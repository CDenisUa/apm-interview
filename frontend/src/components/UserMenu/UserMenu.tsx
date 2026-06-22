// Core
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
// Hooks
import { useAuth } from '../../hooks/useAuth/useAuth'
// Styles
import './UserMenu.css'

const initials = (name: string): string => {
  const parts = name.trim().split(/\s+/)
  return ((parts[0]?.[0] ?? '') + (parts[1]?.[0] ?? '')).toUpperCase()
}

const UserMenu = () => {
  const { t } = useTranslation()
  const { user, login, logout } = useAuth()
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')

  if (!user) {
    return (
      <div className="user-menu">
        <button className="user-menu__signin" onClick={() => setOpen((o) => !o)}>
          {t('userMenu.signIn')}
        </button>
        {open && (
          <div className="user-menu__pop user-menu__pop--right">
            <span className="user-menu__label">{t('userMenu.signInAs')}</span>
            <form
              className="user-menu__form"
              onSubmit={(e) => {
                e.preventDefault()
                if (name.trim()) {
                  login(name)
                  setName('')
                  setOpen(false)
                }
              }}
            >
              <input
                className="user-menu__input"
                placeholder={t('userMenu.namePlaceholder')}
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoFocus
              />
              <button type="submit" className="user-menu__continue">
                {t('userMenu.continue')}
              </button>
            </form>
            <p className="user-menu__hint">{t('userMenu.hint')}</p>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="user-menu">
      <button className="user-menu__trigger" onClick={() => setOpen((o) => !o)}>
        <span className="user-menu__avatar">{initials(user.name)}</span>
        <span className="user-menu__name">{user.name}</span>
      </button>
      {open && (
        <div className="user-menu__pop user-menu__pop--right">
          <div className="user-menu__id">
            <span className="user-menu__avatar user-menu__avatar--lg">{initials(user.name)}</span>
            <div>
              <div className="user-menu__name-lg">{user.name}</div>
              <div className="user-menu__email">{user.email}</div>
            </div>
          </div>
          <button
            className="user-menu__logout"
            onClick={() => {
              logout()
              setOpen(false)
            }}
          >
            {t('userMenu.signOut')}
          </button>
        </div>
      )}
    </div>
  )
}

export default UserMenu
