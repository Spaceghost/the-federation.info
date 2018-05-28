<template>
    <tr>
        <th>
            <router-link
                :to="{name: 'platform', params: {platform: platform.name}}"
            >
                {{ platform.displayName ? platform.displayName : platform.name }}
            </router-link>
        </th>
        <td>
            {{ nodeCount }}
        </td>
        <td>
            <div v-if="statsPlatformToday">
                {{ statsPlatformToday.usersTotal }}
            </div>
        </td>
        <td>
            <a
                v-if="platform.website"
                :href="platform.website"
                target="_blank"
                rel="noopener noreferrer"
            >
                {{ websiteWithoutProtocol }}
            </a>
        </td>
        <td>
            <a
                v-if="platform.code && platform.license"
                :href="platform.code"
                target="_blank"
                rel="noopener noreferrer"
            >
                {{ platform.license }}
            </a>
        </td>
    </tr>
</template>

<script>
import gql from 'graphql-tag'


const platformStatsQuery = gql`
    query PlatformStats($name: String!) {
        statsPlatformToday(name: $name) {
            usersTotal
        }
    }
`

export default {
    apollo: {
        statsPlatformToday: {
            query: platformStatsQuery,
            variables() {
                return {
                    name: this.platform.name,
                }
            },
        },
    },
    name: "PlatformTableRow",
    props: {
        platform: {
            type: Object,
            default: null,
        },
        nodes: {
            type: Array,
            default: () => [],
        },
    },
    data() {
        return {
            statsPlatformToday: {},
        }
    },
    computed: {
        nodeCount() {
            return this.nodes.filter(node => node.platform.name === this.platform.name).length
        },
        websiteWithoutProtocol() {
            return this.platform.website.replace('https://', '').replace('http://', '')
        },
    },
}
</script>