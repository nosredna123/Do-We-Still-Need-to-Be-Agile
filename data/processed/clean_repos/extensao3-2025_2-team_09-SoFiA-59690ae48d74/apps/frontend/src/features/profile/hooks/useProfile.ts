import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { toast } from 'sonner'
import { useUserStore } from '@/stores/userStore'
import { useUpdateUser } from '@/features/auth/hooks/useUser.ts'
import { type ProfileFormValues, profileSchema } from '@/features/profile/types'
import { recurrenceService } from '@/features/dashboard/services/recurrenceService'
import { useQueryClient } from '@tanstack/react-query'
import { formatters } from '@/lib/formatters'

export function useProfile() {
  const user = useUserStore((state) => state.user)
  const { mutateAsync: updateUser } = useUpdateUser()
  const queryClient = useQueryClient()

  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: '',
      api_key: '',
      profile_pic: '',
      salary: '',
      payday: '',
    },
  })

  // Sync form with user state when user loads
  useEffect(() => {
    if (user) {
      // Logic to handle the new nested salary structure
      let salaryString = ''
      let paydayString = ''

      if (user.salary) {
        // Amount comes as cents (integer), convert to float for input
        salaryString = formatters.fromCents(user.salary.amount).toString()
        paydayString = user.salary.payday.toString()
      }

      form.reset({
        name: user.name || '',
        api_key: user.api_key || '',
        profile_pic: user.profile_pic || '',
        salary: salaryString,
        payday: paydayString,
      })
    }
  }, [user, form])

  const handleSubmit = async (data: ProfileFormValues) => {
    try {
      const promises = []

      // 1. Update basic user profile
      promises.push(
        updateUser({
          name: data.name,
          api_key: data.api_key || undefined,
          profile_pic: data.profile_pic || undefined,
        })
      )

      // 2. Handle Salary Logic
      const salaryValue =
        data.salary && data.salary.trim() !== ''
          ? parseFloat(data.salary)
          : null
      const paydayValue =
        data.payday && data.payday.trim() !== '' ? parseInt(data.payday) : null

      if (salaryValue !== null && paydayValue !== null) {
        // Convert input float back to cents
        const amountInCents = Math.round(salaryValue * 100)

        if (user?.salary_recurrence_id) {
          // UPDATE existing recurrence
          promises.push(
            recurrenceService.updateRecurrence(user.salary_recurrence_id, {
              amount: amountInCents,
              day: paydayValue,
              description: 'Salário',
              transaction_type: 'income',
              frequency: 'monthly',
            })
          )
        } else {
          promises.push(
            recurrenceService.createRecurrence(
              recurrenceService.createSalaryPayload(amountInCents, paydayValue)
            )
          )
        }
      }

      await Promise.all(promises)
      await queryClient.invalidateQueries({ queryKey: ['me'] })

      toast.success('Perfil atualizado com sucesso!')
    } catch (error) {
      console.error(error)
    }
  }

  const memberSince = user?.created_at
    ? new Date(user.created_at).toLocaleDateString('pt-BR', {
        month: 'long',
        year: 'numeric',
      })
    : 'Data desconhecida'

  const onSubmit = form.handleSubmit(handleSubmit)

  return {
    user,
    form,
    isPending: form.formState.isSubmitting,
    memberSince,
    onSubmit,
  }
}
