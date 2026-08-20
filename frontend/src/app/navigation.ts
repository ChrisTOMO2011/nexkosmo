export const APP_NAVIGATION_EVENT = "nexkosmo:navigate";

export type AppNavigationDetail = {
  href: string;
  replace?: boolean;
};

export function navigateInApp(href: string, replace = false) {
  window.dispatchEvent(
    new CustomEvent<AppNavigationDetail>(APP_NAVIGATION_EVENT, {
      detail: { href, replace },
    }),
  );
}

