import { expect, type Page } from '@playwright/test';

export type ChargeInput = {
  price: number;
  start: string; // 'YYYY-MM-DD'
  end?: string; // 해지하지 않았으면 생략
  month: string; // 'YYYY-MM'
  coupon?: { kind: 'fixed' | 'percent'; value: number };
};

/**
 * 요금 계산 화면의 페이지 객체 (Page Object Model).
 * 화면의 어떤 칸을 어떻게 찾는지는 여기에만 둡니다.
 * 화면 글자가 바뀌면 테스트가 아니라 이 파일 한 곳만 고칩니다.
 */
export class ChargePage {
  constructor(private readonly page: Page) {}

  async open() {
    await this.page.goto('/');
  }

  async fill(input: ChargeInput) {
    await this.page.getByLabel('월 요금(원)').fill(String(input.price));
    await this.page.getByLabel('이용 시작일').fill(input.start);
    if (input.end) {
      await this.page.getByLabel('이용 종료일').fill(input.end);
    }
    await this.page.getByLabel('청구월').fill(input.month);
    if (input.coupon) {
      await this.page.getByRole('combobox').selectOption(input.coupon.kind);
      await this.page.getByLabel('쿠폰 값').fill(String(input.coupon.value));
    }
  }

  async calculate() {
    await this.page.getByRole('button', { name: '계산' }).click();
  }

  async expectCharge(amount: string) {
    await expect(this.page.getByRole('status')).toHaveText(`청구 금액: ${amount}`);
  }
}
