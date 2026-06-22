// Core
import type { FC } from 'react'
import { useTranslation } from 'react-i18next'
// Styles
import './NewTaskPage.css'

const NewTaskPage: FC = () => {
  const { t } = useTranslation()
  return <div>{t('newTask.title')}</div>
}

export default NewTaskPage
