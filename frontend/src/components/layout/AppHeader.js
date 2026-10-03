export default function AppHeader({
  onMenuToggle,
  userName = "User",
  onLogout,
}) {
  return (
    <header className="flex flex-col gap-3 border-b border-[#2d3748] bg-[#111827] px-3 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-4 md:px-5 xl:px-8">
      <div className="flex items-center gap-3 sm:w-auto">
        <button
          type="button"
          aria-label="Toggle menu"
          onClick={onMenuToggle}
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-[#374151] bg-[#0f172a] text-slate-200 shadow-sm transition hover:bg-[#182335] lg:hidden"
        >
          <span className="flex flex-col gap-1.5">
            <span className="h-0.5 w-5 rounded-full bg-current" />
            <span className="h-0.5 w-5 rounded-full bg-current" />
            <span className="h-0.5 w-5 rounded-full bg-current" />
          </span>
        </button>
      </div>

      <div className="flex items-center justify-end gap-3 sm:ml-4 sm:gap-4">
        <div className="flex items-center gap-3 rounded-xl bg-[#0f172a] px-2 py-2 shadow-sm ring-1 ring-[#374151]">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#f97316] text-sm font-bold text-white">
            {userName.charAt(0).toUpperCase()}
          </div>
          <div className="hidden text-right sm:block">
            <div className="text-[0.9rem] font-semibold text-slate-100">{userName}</div>
          </div>
          {onLogout && (
            <button
              type="button"
              onClick={onLogout}
              className="rounded-lg border border-[#374151] px-3 py-1.5 text-sm font-medium text-slate-200 transition hover:bg-[#182335]"
            >
              Log out
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
