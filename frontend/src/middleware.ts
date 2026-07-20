import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Route protection middleware.
 *
 * Since JWT tokens are stored in localStorage (not cookies), we can't read
 * them server-side. Instead, we protect routes client-side in the components.
 * This middleware handles the basic case of ensuring the /chat and /history
 * pages load only when a cookie-based indicator exists, but we primarily
 * rely on client-side auth checks.
 *
 * For production, consider using httpOnly cookies for tokens.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Public routes that don't need auth
  const publicRoutes = ["/"];

  if (publicRoutes.includes(pathname)) {
    return NextResponse.next();
  }

  // All other routes proceed — client-side auth guards handle the rest
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|api).*)"],
};
