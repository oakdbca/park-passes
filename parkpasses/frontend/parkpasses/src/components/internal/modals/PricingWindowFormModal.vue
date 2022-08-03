<template>
    <div class="modal fade" id="pricingWindowModal" tabindex="-1" aria-labelledby="pricingWindowModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <form @submit.prevent="validateForm" @keydown.enter="$event.preventDefault()" class="needs-validation" novalidate>
                    <div class="modal-header">
                        <h5 class="modal-title" id="pricingWindowModalLabel">Add a New Pricing Window</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="pass-type" class="col-form-label">Pass Type:</label>
                            <select @change="fetchDefaultOptionsForPassType" class="form-control" :class="errors.pass_type ? 'is-invalid' : ''"
                                v-model="pricing_window.pass_type" aria-describedby="validationServerPassTypeFeedback"
                                required>
                                <option value="0" selected="selected" disabled="disabled">Select a Pass Type</option>
                                <option v-for="passType in passTypesDistinct" :value="passType.code">{{
                                        passType.description
                                }}</option>
                            </select>
                            <div v-if="errors.pass_type" id="validationServerPassTypeFeedback" class="invalid-feedback">
                                <p v-for="(error, index) in errors.pass_type" :key="index">{{ error }}</p>
                            </div>
                            <div v-else id="validationServerPassTypeFeedback" class="invalid-feedback">
                                Please select a pass type.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="name" class="col-form-label">Name:</label>
                            <input type="text" class="form-control" :class="errors.name ? 'is-invalid' : ''" id="name"
                                name="name" v-model="pricing_window.name"
                                aria-describedby="validationServerNameFeedback" required />
                            <div v-if="errors.name" id="validationServerNameFeedback" class="invalid-feedback">
                                <p v-for="(error, index) in errors.name" :key="index">{{ error }}</p>
                            </div>
                            <div v-else id="validationServerNameFeedback" class="invalid-feedback">
                                Please enter a name for the pricing window.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="datetimeStart" class="col-form-label">Date Start</label>
                            <input type="date" class="form-control"
                                :class="errors.date_start ? 'is-invalid' : ''" id="datetimeStart"
                                name="datetimeStart" v-model="pricing_window.date_start" required="required"
                                :min="startDate()" aria-describedby="validationServerDateStartFeedback">
                            <div v-if="errors.date_start"  id="validationServerDateStartFeedback" class="invalid-feedback">
                                <p v-for="(error, index) in errors.date_start" :key="index">{{ error }}</p>
                            </div>
                            <div v-else id="validationServerDateStartFeedback" class="invalid-feedback">
                                Please enter a valid start date.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="datetimeExpiry" class="col-form-label">Date End</label>
                            <input type="date" class="form-control"
                                :class="errors.date_expiry ? 'is-invalid' : ''" id="datetimeExpiry"
                                name="datetimeExpiry" v-model="pricing_window.date_expiry" required="required"
                                :min="minEndDate" aria-describedby="validationServerDateExpiryFeedback">
                            <div v-if="errors.date_expiry"  id="validationServerDateExpiryFeedback" class="invalid-feedback">
                                <p v-for="(error, index) in errors.date_expiry" :key="index">{{ error }}</p>
                            </div>
                            <div v-else id="validationServerDateExpiryFeedback" class="invalid-feedback">
                                Please enter a valid end date.
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="submit" class="btn licensing-btn-primary">Submit</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints, helpers } from '@/utils/hooks'

export default {
    name: 'PricingWindowFormModal',
    emits: ['saveSuccess'],
    props: {
        passTypesDistinct: Array,
    },
    data() {
        return {
            pricing_window: this.getPricingWindowInitialState(),
            errors: {},
        }
    },
    computed: {
        minEndDate: function () {
            let endDate = new Date(this.pricing_window.date_start);
            endDate.setDate(endDate.getDate() + 1);
            return endDate;
        }
    },
    methods: {
        startDate: function () {
            const today = new Date();
            return today.toISOString().split('T')[0];
        },
        fetchDefaultOptionsForPassType: function () {

        },
        getPricingWindowInitialState() {
            return {
                pass_type: 0,
                name: '',
                date_start: this.startDate(),
                date_expiry: '',
            }
        },
        submitForm: function () {
            let vm = this;
            vm.pricing_window.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.pricing_window)
            };
            fetch(api_endpoints.savePricingWindow, requestOptions)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        this.errors = data;
                        return Promise.reject(error);
                    }
                    console.log('data = ' + JSON.stringify(data));
                    this.$emit("saveSuccess", {
                            message: 'Pricing Window created successfully.',
                            pricingWindow: data,
                        }
                    );
                    $('#successMessageAlert').show();
                    vm.pricing_window = vm.getPricingWindowInitialState();
                    var PricingWindowFormModalModal = bootstrap.Modal.getInstance(document.getElementById('pricingWindowModal'));
                    PricingWindowFormModalModal.hide();
                })
                .catch(error => {
                    this.systemErrorMessage = "ERROR: Please try again in an hour.";
                    console.error("There was an error!", error);
                }).finally(() =>{

                });
            return false;
        },
        validateForm: function () {
            let vm = this;
            var forms = document.querySelectorAll('.needs-validation');
            Array.prototype.slice.call(forms)
                .forEach(function (form) {
                    if (form.checkValidity()) {
                        vm.submitForm();
                    } else {
                        form.classList.add('was-validated');
                        $(".invalid-feedback:visible:first").siblings('input').focus();
                    }
                });
            return false;
        }
    }
}
</script>