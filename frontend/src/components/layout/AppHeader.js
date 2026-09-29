import { FiBell, FiSearch } from "react-icons/fi";

export default function AppHeader({
  onMenuToggle,
  userName = "User",
  searchPlaceholder = "Search jobs, docs, or templates...",
  onLogout,
}) {
  return (
    <header className="flex flex-col gap-3 border-b border-[#f0dfd3] bg-[#fffaf7] px-3 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-4 md:px-5 xl:px-8">
      <div className="flex items-center gap-3 sm:w-auto">
        <button
          type="button"
          aria-label="Toggle menu"
          onClick={onMenuToggle}
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-[#f3d7c6] bg-white text-[#40465a] shadow-sm transition hover:bg-[#fff4ee] lg:hidden"
        >
          <span className="flex flex-col gap-1.5">
            <span className="h-0.5 w-5 rounded-full bg-current" />
            <span className="h-0.5 w-5 rounded-full bg-current" />
            <span className="h-0.5 w-5 rounded-full bg-current" />
          </span>
        </button>

        <div className="relative w-full max-w-full sm:max-w-[420px]">
          <FiSearch className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[#7a818c]" />
          <input
            type="text"
            placeholder={searchPlaceholder}
            className="h-11 w-full rounded-xl border border-[#f2d8c4] bg-[#fff3ee] pl-11 pr-4 text-sm text-[#505763] placeholder:text-[#8d6d5d] outline-none focus:border-[#f5a66a] focus:bg-white"
          />
        </div>
      </div>

      <div className="flex items-center justify-end gap-3 sm:ml-4 sm:gap-4">
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-[#f3d7c6] bg-white text-[#40465a] shadow-sm transition hover:bg-[#fff4ee]"
        >
          <FiBell className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-3 rounded-xl bg-white px-2 py-2 shadow-sm ring-1 ring-[#f0d9c7]">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#f56d2a] text-sm font-bold text-white">
            {userName.charAt(0).toUpperCase()}
          </div>
          <div className="hidden text-right sm:block">
            <div className="text-[0.9rem] font-semibold text-[#20252d]">{userName}</div>
          </div>
          {onLogout && (
            <button
              type="button"
              onClick={onLogout}
              className="rounded-lg border border-[#f3d7c6] px-3 py-1.5 text-sm font-medium text-[#40465a] transition hover:bg-[#fff4ee]"
            >
              Log out
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
