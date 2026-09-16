import { useUIStore } from '@/stores/uiStore'
import { OnboardingModal } from '@/features/auth/components/OnboardingModal'

export function ModalLayer() {
  const activeModal = useUIStore(
    (state: { activeModal: unknown }) => state.activeModal
  )
  if (!activeModal) return null

  return (
    <>
      {activeModal === 'onboarding' && <OnboardingModal />}
    </>
  )
}
