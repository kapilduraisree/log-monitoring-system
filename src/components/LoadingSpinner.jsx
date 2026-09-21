export default function LoadingSpinner({ size = 'md' }) {
  const sz = { sm: 'h-4 w-4', md: 'h-8 w-8', lg: 'h-12 w-12' }[size]
  return (
    <div className="flex justify-center items-center p-8">
      <div className={`${sz} animate-spin rounded-full border-2 border-slate-600 border-t-blue-500`} />
    </div>
  )
}
