
import { RouterView } from 'vue-router'
import InternalDashboard from '@/components/internal/Dashboard.vue'

import InternalPricingWindows from '@/components/internal/PricingWindows.vue'
import InternalPassForm from '@/components/internal/forms/PassForm.vue'
import InternalDiscountCodeBatchForm from '@/components/internal/forms/DiscountCodeBatchForm.vue'

import InternalVouchers from '@/components/internal/Vouchers.vue'
import InternalDiscountCodes from '@/components/internal/DiscountCodes.vue'
import InternalReports from '@/components/internal/Reports.vue'

export default {
    path: '/internal',
    component: RouterView,
    children: [
        {
            path: '/internal/',
            component: InternalDashboard,
            name: 'internal-dash'
        },
        {
            path: '/internal/pricing-windows',
            component: InternalPricingWindows,
            name: 'internal-pricing-windows'
        },
        {
            path: '/internal/passes/:passId',
            component: InternalPassForm,
            name: 'internal-pass-form'
        },
        {
            path: '/internal/vouchers',
            component: InternalVouchers,
            name: 'internal-vouchers'
        },
        {
            path: '/internal/discount-codes',
            component: InternalDiscountCodes,
            name: 'internal-discount-codes'
        },
        {
            path: '/internal/reports',
            component: InternalReports,
            name: 'internal-reports'
        },
        {
            path: '/internal/discount-code-batch-form/:discountCodeBatchId',
            component: InternalDiscountCodeBatchForm,
            name: 'internal-discount-code-batch-form'
        },
    ]
}
