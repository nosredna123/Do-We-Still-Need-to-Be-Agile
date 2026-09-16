export const formatters = {
  /**
   * Converts a value in cents (integer) to a float (decimal).
   * Example: 1550 -> 15.50
   */
  fromCents: (amount: number): number => {
    return amount / 100
  },

  /**
   * Formats a number as BRL currency.
   * Example: 15.50 -> R$ 15,50
   */
  currency: (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value)
  },
}
